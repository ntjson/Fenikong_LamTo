# Generated manually for report photo content-hash uniqueness.

from django.db import migrations, models


def backfill_content_sha(apps, schema_editor):
    ReportPhoto = apps.get_model("maintenance", "ReportPhoto")
    for rp in ReportPhoto.objects.select_related("version").iterator():
        sha = getattr(rp.version, "sha256", "") or ""
        ReportPhoto.objects.filter(pk=rp.pk).update(content_sha=sha)


class Migration(migrations.Migration):

    dependencies = [
        ("maintenance", "0013_issuereport_client_ref"),
    ]

    operations = [
        migrations.AddField(
            model_name="reportphoto",
            name="content_sha",
            field=models.CharField(default="", max_length=64),
            preserve_default=False,
        ),
        migrations.RunPython(backfill_content_sha, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name="reportphoto",
            constraint=models.UniqueConstraint(
                fields=("report", "content_sha"),
                name="report_photo_content_sha_once",
            ),
        ),
    ]
