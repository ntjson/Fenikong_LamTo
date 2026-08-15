"""Backfill outbox building from the signer's organization, teach the insert
procedure to stamp it, and make it immutable in the identity trigger.

Building derivation rule (spec 2.2): signer wallet -> membership ->
organization -> building. Signing capability is per-building membership, so
the signer's organization building is the anchored record's building.

CREATE OR REPLACE on the SECURITY DEFINER insert procedure requires the
service-role owner (lamto_service); plain RunSQL as the app role fails.
"""

import os

from django.db import migrations

INSERT_FUNCTION_WITH_BUILDING = """
CREATE OR REPLACE FUNCTION lamto_security.evidence_insert_outbox_event(
    p_event_id text, p_event_type smallint, p_payload jsonb, p_payload_hash text,
    p_previous_hash text, p_signature text, p_wallet_id bigint, p_membership_id bigint,
    p_canonical_payload text, p_authorization text
) RETURNS bigint
LANGUAGE plpgsql SECURITY DEFINER SET search_path = pg_catalog, public AS $$
DECLARE event_pk bigint; v_building_id bigint;
BEGIN
    IF p_payload IS DISTINCT FROM p_canonical_payload::jsonb THEN
        RAISE EXCEPTION 'canonical evidence payload does not match the queued payload'
        USING ERRCODE = 'check_violation';
    END IF;
    IF p_authorization IS DISTINCT FROM (
        SELECT encode(
            sha256(
                secret || sha256(
                    secret ||
                    convert_to(
                        format(
                        'evidence-queue|%s|%s|%s|%s|%s|%s|%s|%s',
                        p_event_id, p_event_type, p_payload_hash, p_previous_hash,
                        p_signature, p_wallet_id, p_membership_id, p_canonical_payload
                        ),
                        'UTF8'
                    )
                )
            ),
            'hex'
        )
        FROM lamto_security.write_authorization_secret
        WHERE id = TRUE
    ) THEN
        RAISE EXCEPTION 'evidence queue authorization is invalid'
        USING ERRCODE = 'insufficient_privilege';
    END IF;
    PERFORM 1 FROM public.accounts_organizationmembership
    WHERE id = p_membership_id AND active
      AND role IN ('OPERATOR', 'BOARD', 'RESIDENT_REP') FOR UPDATE;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'membership is not eligible to queue evidence'
        USING ERRCODE = 'insufficient_privilege';
    END IF;
    PERFORM 1 FROM public.accounts_signerwallet
    WHERE id = p_wallet_id AND membership_id = p_membership_id AND active FOR UPDATE;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'wallet is not active for the membership'
        USING ERRCODE = 'insufficient_privilege';
    END IF;
    SELECT o.building_id INTO v_building_id
    FROM public.accounts_organizationmembership m
    JOIN public.accounts_organization o ON o.id = m.organization_id
    WHERE m.id = p_membership_id;
    IF v_building_id IS NULL THEN
        RAISE EXCEPTION 'membership has no organization building'
        USING ERRCODE = 'check_violation';
    END IF;
    INSERT INTO public.evidence_blockchainoutboxevent
        (event_id, event_type, payload, payload_hash, previous_hash, signature,
         signer_wallet_id, building_id, status, attempts, next_attempt_at,
         lease_expires_at, last_attempt_at, transaction_hash, receipt_status,
         receipt, last_error, chain_confirmed_block, chain_block_timestamp,
         submitted_at, confirmed_at, created_at, updated_at)
    VALUES
        (p_event_id, p_event_type, p_payload, p_payload_hash, p_previous_hash,
         p_signature, p_wallet_id, v_building_id, 'PENDING', 0, NULL, NULL, NULL,
         '', NULL, '{}'::jsonb, '', NULL, NULL, NULL, NULL,
         clock_timestamp(), clock_timestamp())
    RETURNING id INTO event_pk;
    RETURN event_pk;
END;
$$;
REVOKE ALL ON FUNCTION lamto_security.evidence_insert_outbox_event(
    text, smallint, jsonb, text, text, text, bigint, bigint, text, text
) FROM PUBLIC;
"""

IDENTITY_TRIGGER_WITH_BUILDING = """
CREATE OR REPLACE FUNCTION evidence_protect_outbox_identity()
RETURNS trigger AS $$
DECLARE service_owner name;
BEGIN
    SELECT pg_get_userbyid(proowner) INTO service_owner
    FROM pg_proc WHERE oid = 'lamto_security.evidence_insert_outbox_event(text,smallint,jsonb,text,text,text,bigint,bigint,text,text)'::regprocedure;
    IF TG_OP = 'INSERT' THEN
        IF current_user IS DISTINCT FROM service_owner THEN
            RAISE EXCEPTION 'outbox inserts require the queue procedure'
            USING ERRCODE = 'check_violation';
        END IF;
        RETURN NEW;
    END IF;
    IF TG_OP = 'DELETE' OR OLD.event_id IS DISTINCT FROM NEW.event_id
       OR OLD.event_type IS DISTINCT FROM NEW.event_type
       OR OLD.payload IS DISTINCT FROM NEW.payload
       OR OLD.payload_hash IS DISTINCT FROM NEW.payload_hash
       OR OLD.previous_hash IS DISTINCT FROM NEW.previous_hash
       OR OLD.signer_wallet_id IS DISTINCT FROM NEW.signer_wallet_id
       OR OLD.building_id IS DISTINCT FROM NEW.building_id
       OR OLD.signature IS DISTINCT FROM NEW.signature
       OR OLD.created_at IS DISTINCT FROM NEW.created_at THEN
        RAISE EXCEPTION 'signed outbox identity is immutable'
        USING ERRCODE = 'check_violation';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
"""

INSERT_FUNCTION_WITHOUT_BUILDING = INSERT_FUNCTION_WITH_BUILDING.replace(
    """    SELECT o.building_id INTO v_building_id
    FROM public.accounts_organizationmembership m
    JOIN public.accounts_organization o ON o.id = m.organization_id
    WHERE m.id = p_membership_id;
    IF v_building_id IS NULL THEN
        RAISE EXCEPTION 'membership has no organization building'
        USING ERRCODE = 'check_violation';
    END IF;
""",
    "",
).replace(
    "signer_wallet_id, building_id, status", "signer_wallet_id, status"
).replace(
    "p_signature, p_wallet_id, v_building_id, 'PENDING'", "p_signature, p_wallet_id, 'PENDING'"
).replace(
    "DECLARE event_pk bigint; v_building_id bigint;", "DECLARE event_pk bigint;"
)

IDENTITY_TRIGGER_WITHOUT_BUILDING = IDENTITY_TRIGGER_WITH_BUILDING.replace(
    "       OR OLD.building_id IS DISTINCT FROM NEW.building_id\n", ""
)


def _as_service_role(schema_editor, sql):
    service_role = os.getenv("POSTGRES_SERVICE_ROLE") or "lamto_service"
    quote_name = schema_editor.connection.ops.quote_name
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("SET ROLE " + quote_name(service_role))
        try:
            cursor.execute(sql)
        finally:
            cursor.execute("RESET ROLE")


def grant_organization_select(apps, schema_editor):
    """SECURITY DEFINER insert procedure joins organization for building_id."""
    service_role = os.getenv("POSTGRES_SERVICE_ROLE") or "lamto_service"
    quote_name = schema_editor.connection.ops.quote_name
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            "GRANT SELECT ON TABLE accounts_organization TO "
            + quote_name(service_role)
        )


def apply_insert_with_building(apps, schema_editor):
    _as_service_role(schema_editor, INSERT_FUNCTION_WITH_BUILDING)


def reverse_insert_without_building(apps, schema_editor):
    _as_service_role(schema_editor, INSERT_FUNCTION_WITHOUT_BUILDING)


def apply_identity_with_building(apps, schema_editor):
    # Trigger function lives in public and is not service-owned; app role can replace it.
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(IDENTITY_TRIGGER_WITH_BUILDING)


def reverse_identity_without_building(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(IDENTITY_TRIGGER_WITHOUT_BUILDING)


def backfill_building(apps, schema_editor):
    Event = apps.get_model("evidence", "BlockchainOutboxEvent")
    for event in (
        Event.objects.select_related("signer_wallet__membership__organization")
        .filter(building__isnull=True)
        .iterator()
    ):
        event.building_id = event.signer_wallet.membership.organization.building_id
        event.save(update_fields=["building"])


class Migration(migrations.Migration):
    dependencies = [("evidence", "0008_outbox_building")]

    operations = [
        migrations.RunPython(grant_organization_select, migrations.RunPython.noop),
        migrations.RunPython(apply_insert_with_building, reverse_insert_without_building),
        migrations.RunPython(backfill_building, migrations.RunPython.noop),
        migrations.RunPython(apply_identity_with_building, reverse_identity_without_building),
    ]
