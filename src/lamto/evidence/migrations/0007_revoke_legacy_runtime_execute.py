import os

from django.db import migrations


def revoke_application_execute(apps, schema_editor):
    application_role = os.getenv("POSTGRES_APPLICATION_ROLE") or os.getenv("POSTGRES_USER")
    if not application_role:
        return
    quote_name = schema_editor.connection.ops.quote_name
    signatures = (
        "text, smallint, jsonb, text, text, text, bigint, bigint, text, text",
        "text, smallint, jsonb, text, text, text, bigint, bigint, text",
        "text, smallint, jsonb, text, text, text, bigint, bigint",
    )
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("SELECT current_user")
        current_user = cursor.fetchone()[0]
        if application_role == current_user:
            return
        cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", [application_role])
        if cursor.fetchone() is None:
            raise RuntimeError(f"PostgreSQL application role {application_role!r} does not exist.")
        for signature in signatures:
            procedure = "lamto_security.evidence_insert_outbox_event(" + signature + ")"
            cursor.execute("SELECT to_regprocedure(%s)", [procedure])
            if cursor.fetchone()[0] is not None:
                cursor.execute(
                    "REVOKE EXECUTE ON FUNCTION " + procedure + " FROM "
                    + quote_name(application_role)
                )


class Migration(migrations.Migration):
    dependencies = [("evidence", "0006_grant_signed_executor")]

    operations = [
        migrations.RunPython(revoke_application_execute, migrations.RunPython.noop),
    ]
