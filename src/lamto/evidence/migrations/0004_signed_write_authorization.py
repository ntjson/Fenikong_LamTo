import os

from django.db import migrations


def provision_outbox_authorization(apps, schema_editor):
    service_role = os.getenv("POSTGRES_SERVICE_ROLE") or "lamto_service"
    executor_role = os.getenv("POSTGRES_EXECUTOR_ROLE") or "lamto_writer"
    quote_name = schema_editor.connection.ops.quote_name
    quoted_service_role = quote_name(service_role)
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("SELECT current_user")
        current_role = quote_name(cursor.fetchone()[0])
        cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", [service_role])
        if cursor.fetchone() is None:
            raise RuntimeError(f"PostgreSQL service role {service_role!r} does not exist.")
        if executor_role:
            if executor_role == service_role:
                raise RuntimeError("POSTGRES_EXECUTOR_ROLE must be different from POSTGRES_SERVICE_ROLE.")
            cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", [executor_role])
            if cursor.fetchone() is None:
                raise RuntimeError(f"PostgreSQL executor role {executor_role!r} does not exist.")
            cursor.execute(
                "GRANT EXECUTE ON FUNCTION lamto_security.evidence_insert_outbox_event("
                "text, smallint, jsonb, text, text, text, bigint, bigint, text, text) TO "
                + quote_name(executor_role)
            )
        cursor.execute(
            "GRANT SELECT ON TABLE lamto_security.write_authorization_secret TO "
            + quoted_service_role
        )
        cursor.execute(
            "ALTER FUNCTION lamto_security.evidence_insert_outbox_event("
            "text, smallint, jsonb, text, text, text, bigint, bigint, text, text) OWNER TO "
            + quoted_service_role
        )
        cursor.execute("SET ROLE " + quoted_service_role)
        cursor.execute(
            "GRANT EXECUTE ON FUNCTION lamto_security.evidence_insert_outbox_event("
            "text, smallint, jsonb, text, text, text, bigint, bigint, text, text) TO "
            + current_role
        )
        cursor.execute("RESET ROLE")


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0006_signed_write_authorization"),
        ("evidence", "0003_outbox_write_procedure"),
    ]

    operations = [
        migrations.RunSQL(
            """
            DROP FUNCTION lamto_security.evidence_insert_outbox_event(
                text, smallint, jsonb, text, text, text, bigint, bigint
            );

            CREATE FUNCTION lamto_security.evidence_insert_outbox_event(
                p_event_id text, p_event_type smallint, p_payload jsonb, p_payload_hash text,
                p_previous_hash text, p_signature text, p_wallet_id bigint, p_membership_id bigint,
                p_canonical_payload text, p_authorization text
            ) RETURNS bigint
            LANGUAGE plpgsql SECURITY DEFINER SET search_path = pg_catalog, public AS $$
            DECLARE event_pk bigint;
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
                INSERT INTO public.evidence_blockchainoutboxevent
                    (event_id, event_type, payload, payload_hash, previous_hash, signature,
                     signer_wallet_id, status, attempts, next_attempt_at, lease_expires_at,
                     last_attempt_at, transaction_hash, receipt_status, receipt, last_error,
                     chain_confirmed_block, chain_block_timestamp, submitted_at, confirmed_at,
                     created_at, updated_at)
                VALUES
                    (p_event_id, p_event_type, p_payload, p_payload_hash, p_previous_hash,
                     p_signature, p_wallet_id, 'PENDING', 0, NULL, NULL, NULL, '', NULL,
                     '{}'::jsonb, '', NULL, NULL, NULL, NULL, clock_timestamp(), clock_timestamp())
                RETURNING id INTO event_pk;
                RETURN event_pk;
            END;
            $$;
            REVOKE ALL ON FUNCTION lamto_security.evidence_insert_outbox_event(
                text, smallint, jsonb, text, text, text, bigint, bigint, text, text
            ) FROM PUBLIC;

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
                   OR OLD.signature IS DISTINCT FROM NEW.signature
                   OR OLD.created_at IS DISTINCT FROM NEW.created_at THEN
                    RAISE EXCEPTION 'signed outbox identity is immutable'
                    USING ERRCODE = 'check_violation';
                END IF;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
            """,
            """
            DROP FUNCTION lamto_security.evidence_insert_outbox_event(
                text, smallint, jsonb, text, text, text, bigint, bigint, text, text
            );
            """,
        ),
        migrations.RunPython(provision_outbox_authorization, migrations.RunPython.noop),
    ]
