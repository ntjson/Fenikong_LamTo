from django.db import migrations


def purge_totp_secrets(apps, schema_editor):
    """Drop django-otp TOTP schema and delete every enrolled secret.

    Upgraded databases may still contain the third-party ``otp_totp``
    application schema: the TOTP device table, its content type, and the
    generated model permissions. Dropping the table deletes all confirmed
    and pending enrolled secrets permanently. The content type and
    permission cleanup is idempotent and harmless when django-otp was never
    installed, which keeps this safe on fresh databases.
    """
    connection = schema_editor.connection
    quote_name = connection.ops.quote_name
    with connection.cursor() as cursor:
        cursor.execute("SELECT to_regclass(%s)", ["otp_totp_totpdevice"])
        if cursor.fetchone()[0] is not None:
            cursor.execute("DROP TABLE " + quote_name("otp_totp_totpdevice"))
        cursor.execute(
            "DELETE FROM {permission} WHERE content_type_id IN ("
            "SELECT id FROM {content_type} WHERE app_label IN ('otp_totp', 'django_otp'))".format(
                permission=quote_name("auth_permission"),
                content_type=quote_name("django_content_type"),
            )
        )
        cursor.execute(
            "DELETE FROM {content_type} WHERE app_label IN ('otp_totp', 'django_otp')".format(
                content_type=quote_name("django_content_type")
            )
        )


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0018_registrationrequest"),
    ]

    operations = [
        migrations.RunPython(purge_totp_secrets, migrations.RunPython.noop),
    ]
