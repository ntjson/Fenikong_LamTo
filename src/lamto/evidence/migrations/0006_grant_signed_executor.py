import os

from django.db import migrations


def grant_executor_access(apps, schema_editor):
    executor_role = os.getenv("POSTGRES_EXECUTOR_ROLE") or "lamto_writer"
    service_role = os.getenv("POSTGRES_SERVICE_ROLE") or "lamto_service"
    quote_name = schema_editor.connection.ops.quote_name
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("SELECT current_user")
        current_user = cursor.fetchone()[0]
        if executor_role == service_role:
            raise RuntimeError("POSTGRES_EXECUTOR_ROLE must be different from POSTGRES_SERVICE_ROLE.")
        cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", [service_role])
        if cursor.fetchone() is None:
            raise RuntimeError(f"PostgreSQL service role {service_role!r} does not exist.")
        cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", [executor_role])
        if cursor.fetchone() is None:
            raise RuntimeError(f"PostgreSQL executor role {executor_role!r} does not exist.")
        quoted_executor_role = quote_name(executor_role)
        cursor.execute("GRANT USAGE ON SCHEMA lamto_security TO " + quoted_executor_role)
        cursor.execute(
            "GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO "
            + quoted_executor_role
        )
        cursor.execute(
            "GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO "
            + quoted_executor_role
        )
        cursor.execute(
            "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO "
            + quoted_executor_role
        )
        cursor.execute(
            "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO "
            + quoted_executor_role
        )
        cursor.execute(
            "REVOKE INSERT, DELETE, TRUNCATE ON accounts_signerwallet, "
            "accounts_signerauthorizationrequest, evidence_blockchainoutboxevent FROM "
            + quoted_executor_role
        )
        cursor.execute(
            "REVOKE UPDATE ON accounts_signerwallet, accounts_signerauthorizationrequest, "
            "evidence_blockchainoutboxevent FROM " + quoted_executor_role
        )
        cursor.execute(
            "GRANT UPDATE ON accounts_signerwallet TO " + quoted_executor_role
        )
        cursor.execute(
            "GRANT UPDATE (status, transaction_hash, last_error, confirmed_at) "
            "ON accounts_signerauthorizationrequest TO " + quoted_executor_role
        )
        cursor.execute(
            "GRANT UPDATE (status, attempts, next_attempt_at, lease_expires_at, "
            "last_attempt_at, transaction_hash, receipt_status, receipt, last_error, "
            "chain_confirmed_block, chain_block_timestamp, submitted_at, confirmed_at, updated_at) "
            "ON evidence_blockchainoutboxevent TO " + quoted_executor_role
        )
        signatures = (
            "text, smallint, jsonb, text, text, text, bigint, bigint, text, text",
            "text, smallint, jsonb, text, text, text, bigint, bigint, text",
            "text, smallint, jsonb, text, text, text, bigint, bigint",
        )
        cursor.execute("SET ROLE " + quote_name(service_role))
        for signature in signatures:
            cursor.execute(
                "SELECT to_regprocedure(%s)",
                ["lamto_security.evidence_insert_outbox_event(" + signature + ")"],
            )
            if cursor.fetchone()[0] is not None:
                cursor.execute(
                    "GRANT EXECUTE ON FUNCTION lamto_security.evidence_insert_outbox_event("
                    + signature + ") TO " + quoted_executor_role
                )
        cursor.execute("RESET ROLE")


class Migration(migrations.Migration):
    dependencies = [("evidence", "0005_restrict_signed_write_procedures")]

    operations = [
        migrations.RunPython(grant_executor_access, migrations.RunPython.noop),
    ]
