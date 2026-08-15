import os

from django.db import migrations


def revoke_application_execute(apps, schema_editor):
    application_role = os.getenv("POSTGRES_APPLICATION_ROLE") or os.getenv("POSTGRES_USER")
    if not application_role:
        return
    quote_name = schema_editor.connection.ops.quote_name
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("SELECT current_user")
        current_user = cursor.fetchone()[0]
        if application_role == current_user:
            return
        cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", [application_role])
        if cursor.fetchone() is None:
            raise RuntimeError(f"PostgreSQL application role {application_role!r} does not exist.")
        for signature in (
            "lamto_security.evidence_insert_outbox_event(text, smallint, jsonb, text, text, text, bigint, bigint, text, text)",
            "lamto_security.evidence_insert_outbox_event(text, smallint, jsonb, text, text, text, bigint, bigint, text)",
            "lamto_security.evidence_insert_outbox_event(text, smallint, jsonb, text, text, text, bigint, bigint)",
        ):
            cursor.execute("SELECT to_regprocedure(%s)", [signature])
            if cursor.fetchone()[0] is not None:
                cursor.execute(
                    "REVOKE EXECUTE ON FUNCTION " + signature + " FROM "
                    + quote_name(application_role)
                )


class Migration(migrations.Migration):
    dependencies = [("evidence", "0004_signed_write_authorization")]

    operations = [
        migrations.RunPython(revoke_application_execute, migrations.RunPython.noop),
    ]
