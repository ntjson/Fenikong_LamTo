"""Record when case work started, so progress and completion can require it.

``start_case_work`` used to write nothing to the case — it only moved the
linked reports to IN_PROGRESS — so nothing downstream could tell a started
case from an untouched one. Existing rows are backfilled from the evidence
that work did happen: the first work update, else the case's own creation
time for cases whose reports are already IN_PROGRESS or that are completed.
"""

from django.db import migrations, models


def backfill_started_at(apps, schema_editor):
    schema_editor.execute(
        """
        UPDATE maintenance_maintenancecase AS c
        SET started_at = COALESCE(
            (SELECT MIN(u.created_at) FROM maintenance_workupdate AS u WHERE u.case_id = c.id),
            c.created_at
        )
        WHERE c.started_at IS NULL
          AND (
            c.completed_at IS NOT NULL
            OR EXISTS (SELECT 1 FROM maintenance_workupdate AS u WHERE u.case_id = c.id)
            OR EXISTS (
                SELECT 1
                FROM maintenance_casereport AS cr
                JOIN maintenance_issuereport AS r ON r.id = cr.report_id
                WHERE cr.case_id = c.id AND r.status = 'IN_PROGRESS'
            )
          )
        """
    )


class Migration(migrations.Migration):

    dependencies = [
        ("maintenance", "0023_management_queue_vocabulary"),
    ]

    operations = [
        migrations.AddField(
            model_name="maintenancecase",
            name="started_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.RunPython(backfill_started_at, migrations.RunPython.noop),
    ]
