import os

from django.db import migrations


FUNCTION_SQL = r"""
CREATE FUNCTION lamto_security.evidence_insert_platform_outbox_event(
    p_event_id text, p_event_type smallint, p_payload jsonb, p_payload_hash text,
    p_previous_hash text, p_signature text, p_signer_address text, p_building_id bigint,
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
        SELECT encode(sha256(secret || sha256(secret || convert_to(format(
            'platform-evidence-queue|%s|%s|%s|%s|%s|%s|%s|%s',
            p_event_id, p_event_type, p_payload_hash, p_previous_hash,
            p_signature, p_signer_address, p_building_id, p_canonical_payload
        ), 'UTF8'))), 'hex')
        FROM lamto_security.write_authorization_secret WHERE id = TRUE
    ) THEN
        RAISE EXCEPTION 'platform evidence queue authorization is invalid'
        USING ERRCODE = 'insufficient_privilege';
    END IF;
    INSERT INTO public.evidence_blockchainoutboxevent
        (event_id, event_type, payload, payload_hash, previous_hash, signature,
         signer_address, building_id, status, attempts, receipt,
         transaction_hash, last_error, created_at, updated_at)
    VALUES
        (p_event_id, p_event_type, p_payload, p_payload_hash, p_previous_hash,
         p_signature, p_signer_address, p_building_id, 'PENDING', 0, '{}'::jsonb,
         '', '', clock_timestamp(), clock_timestamp())
    RETURNING id INTO event_pk;
    RETURN event_pk;
END;
$$;
"""


def restore_platform_insert(apps, schema_editor):
    service_role = os.getenv("POSTGRES_SERVICE_ROLE") or "lamto_service"
    writer_role = os.getenv("POSTGRES_EXECUTOR_ROLE") or "lamto_writer"
    quote = schema_editor.connection.ops.quote_name
    signature = (
        "lamto_security.evidence_insert_platform_outbox_event("
        "text,smallint,jsonb,text,text,text,text,bigint,text,text)"
    )
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("SELECT current_user")
        current_role = cursor.fetchone()[0]
        cursor.execute("SET ROLE " + quote(service_role))
        try:
            cursor.execute(FUNCTION_SQL)
            cursor.execute("REVOKE ALL ON FUNCTION " + signature + " FROM PUBLIC")
            cursor.execute("GRANT EXECUTE ON FUNCTION " + signature + " TO " + quote(writer_role))
            cursor.execute("GRANT EXECUTE ON FUNCTION " + signature + " TO " + quote(current_role))
        finally:
            cursor.execute("RESET ROLE")
        cursor.execute(r"""
                CREATE OR REPLACE FUNCTION evidence_protect_outbox_identity()
                RETURNS trigger AS $$
                DECLARE service_owner name;
                BEGIN
                    SELECT pg_get_userbyid(proowner) INTO service_owner
                    FROM pg_proc WHERE oid = 'lamto_security.evidence_insert_platform_outbox_event(text,smallint,jsonb,text,text,text,text,bigint,text,text)'::regprocedure;
                    IF TG_OP = 'INSERT' THEN
                        IF current_user IS DISTINCT FROM service_owner THEN
                            RAISE EXCEPTION 'outbox inserts require the platform queue procedure'
                            USING ERRCODE = 'check_violation';
                        END IF;
                        RETURN NEW;
                    END IF;
                    IF TG_OP = 'DELETE' OR OLD.event_id IS DISTINCT FROM NEW.event_id
                       OR OLD.event_type IS DISTINCT FROM NEW.event_type
                       OR OLD.payload IS DISTINCT FROM NEW.payload
                       OR OLD.payload_hash IS DISTINCT FROM NEW.payload_hash
                       OR OLD.previous_hash IS DISTINCT FROM NEW.previous_hash
                       OR OLD.signer_address IS DISTINCT FROM NEW.signer_address
                       OR OLD.building_id IS DISTINCT FROM NEW.building_id
                       OR OLD.signature IS DISTINCT FROM NEW.signature
                       OR OLD.created_at IS DISTINCT FROM NEW.created_at THEN
                        RAISE EXCEPTION 'signed outbox identity is immutable'
                        USING ERRCODE = 'check_violation';
                    END IF;
                    RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;
        """)


class Migration(migrations.Migration):
    dependencies = [("evidence", "0021_blockchainoutboxevent_outbox_signer_address_required")]
    operations = [migrations.RunPython(restore_platform_insert, migrations.RunPython.noop)]
