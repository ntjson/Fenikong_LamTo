import os

from django.db import migrations


def grant_application_role(apps, schema_editor):
    executor_role = os.getenv("POSTGRES_EXECUTOR_ROLE") or "lamto_writer"
    roles = []
    for role in (
        os.getenv("POSTGRES_APPLICATION_ROLE") or os.getenv("POSTGRES_USER"),
        executor_role,
    ):
        if role and role not in roles:
            roles.append(role)
    if not roles:
        return
    with schema_editor.connection.cursor() as cursor:
        for role in roles:
            quoted = schema_editor.connection.ops.quote_name(role)
            cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", [role])
            if cursor.fetchone() is None:
                raise RuntimeError(f"PostgreSQL runtime role {role!r} does not exist.")
            cursor.execute(f"GRANT USAGE ON SCHEMA lamto_security TO {quoted}")
            cursor.execute(f"GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO {quoted}")
            cursor.execute(f"GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO {quoted}")
            cursor.execute(
                f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO {quoted}"
            )
            cursor.execute(
                f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO {quoted}"
            )
            cursor.execute(
                f"REVOKE INSERT, DELETE, TRUNCATE ON accounts_signerwallet, "
                f"accounts_signerauthorizationrequest, evidence_blockchainoutboxevent FROM {quoted}"
            )
            cursor.execute(f"REVOKE UPDATE ON accounts_signerwallet, accounts_signerauthorizationrequest, evidence_blockchainoutboxevent FROM {quoted}")
            if role == executor_role:
                cursor.execute(f"GRANT UPDATE ON accounts_signerwallet TO {quoted}")
            cursor.execute(
                f"GRANT UPDATE (status, transaction_hash, last_error, confirmed_at) "
                f"ON accounts_signerauthorizationrequest TO {quoted}"
            )
            cursor.execute(
                f"GRANT UPDATE (status, attempts, next_attempt_at, lease_expires_at, "
                f"last_attempt_at, transaction_hash, receipt_status, receipt, last_error, "
                f"chain_confirmed_block, chain_block_timestamp, submitted_at, confirmed_at, updated_at) "
                f"ON evidence_blockchainoutboxevent TO {quoted}"
            )
        if executor_role:
            quoted_executor_role = schema_editor.connection.ops.quote_name(executor_role)
            cursor.execute(
                f"GRANT EXECUTE ON FUNCTION lamto_security.evidence_insert_outbox_event("
                f"text, smallint, jsonb, text, text, text, bigint, bigint) TO {quoted_executor_role}"
            )

def provision_evidence_service_owner(apps, schema_editor):
    service_role = os.getenv("POSTGRES_SERVICE_ROLE") or "lamto_service"
    application_role = os.getenv("POSTGRES_APPLICATION_ROLE") or os.getenv("POSTGRES_USER")
    executor_role = os.getenv("POSTGRES_EXECUTOR_ROLE") or "lamto_writer"
    quote_name = schema_editor.connection.ops.quote_name
    quoted_service_role = quote_name(service_role)

    with schema_editor.connection.cursor() as cursor:
        cursor.execute("SELECT current_user")
        if cursor.fetchone()[0] == service_role:
            raise RuntimeError("POSTGRES_SERVICE_ROLE must be different from the migration/application role.")
        cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", [service_role])
        if cursor.fetchone() is None:
            raise RuntimeError(f"PostgreSQL service role {service_role!r} does not exist.")
        cursor.execute(
            "ALTER FUNCTION lamto_security.evidence_insert_outbox_event(text, smallint, jsonb, text, text, text, bigint, bigint) OWNER TO "
            + quoted_service_role
        )
        cursor.execute(
            "GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE evidence_blockchainoutboxevent TO "
            + quoted_service_role
        )
        cursor.execute(
            "GRANT USAGE, SELECT ON SEQUENCE evidence_blockchainoutboxevent_id_seq TO "
            + quoted_service_role
        )
        for role, label in (
            (application_role, "application"),
            (executor_role, "executor"),
        ):
            if role:
                if role == service_role:
                    raise RuntimeError(f"POSTGRES_{label.upper()}_ROLE must be different from POSTGRES_SERVICE_ROLE.")
                cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", [role])
                if cursor.fetchone() is None:
                    raise RuntimeError(f"PostgreSQL {label} role {role!r} does not exist.")


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0005_wallet_write_procedures"),
        ("evidence", "0002_guard_outbox_transitions"),
    ]

    operations = [
        migrations.RunSQL(
            r"""
            CREATE FUNCTION lamto_security.evidence_insert_outbox_event(
                p_event_id text, p_event_type smallint, p_payload jsonb, p_payload_hash text,
                p_previous_hash text, p_signature text, p_wallet_id bigint, p_membership_id bigint
            ) RETURNS bigint
            LANGUAGE plpgsql SECURITY DEFINER SET search_path = pg_catalog, public AS $$
            DECLARE event_pk bigint;
            BEGIN
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
            REVOKE ALL ON FUNCTION lamto_security.evidence_insert_outbox_event(text, smallint, jsonb, text, text, text, bigint, bigint) FROM PUBLIC;

            CREATE OR REPLACE FUNCTION evidence_protect_outbox_identity()
            RETURNS trigger AS $$
            DECLARE service_owner name;
            BEGIN
                SELECT pg_get_userbyid(proowner) INTO service_owner
                FROM pg_proc WHERE oid = 'lamto_security.evidence_insert_outbox_event(text,smallint,jsonb,text,text,text,bigint,bigint)'::regprocedure;
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
            r"""
            DROP FUNCTION lamto_security.evidence_insert_outbox_event(text, smallint, jsonb, text, text, text, bigint, bigint);
            """,
        ),
        migrations.RunPython(grant_application_role, migrations.RunPython.noop),
        migrations.RunPython(provision_evidence_service_owner, migrations.RunPython.noop),
    ]
