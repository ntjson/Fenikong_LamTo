import os

from django.db import migrations


def grant_executor_execute(apps, schema_editor):
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
        cursor.execute("SET ROLE " + quote_name(service_role))
        cursor.execute(
            "GRANT EXECUTE ON FUNCTION lamto_security.accounts_register_signer_wallet(bigint, text, text), "
            "lamto_security.accounts_revoke_signer_wallet(bigint, bigint, text) TO "
            + quote_name(executor_role)
        )
        cursor.execute("RESET ROLE")


class Migration(migrations.Migration):
    dependencies = [("accounts", "0007_restrict_signed_write_procedures")]

    operations = [
        migrations.RunPython(grant_executor_execute, migrations.RunPython.noop),
    ]
