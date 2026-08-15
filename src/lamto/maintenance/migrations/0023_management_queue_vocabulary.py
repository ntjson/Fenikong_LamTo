"""Turn the free-text ``department`` into a closed Management queue (ADR 0003).

Existing values are mapped by normalising to a code; anything unrecognised
becomes GENERAL. The mapping is lossy on purpose — the pilot database is
reseeded, and a free-text column cannot be translated.
"""

from django.db import migrations, models


MODELS = ("triagesuggestion", "triagedecision", "maintenancecase")
TABLES = (
    "maintenance_triagesuggestion",
    "maintenance_triagedecision",
    "maintenance_maintenancecase",
)
KNOWN = (
    "MAINTENANCE", "PLUMBING", "ELECTRICAL", "ELEVATOR", "HVAC",
    "CLEANING", "SECURITY", "LANDSCAPING", "PEST_CONTROL", "GENERAL",
)


def to_codes(apps, schema_editor):
    known = ", ".join(f"'{code}'" for code in KNOWN)
    for table in TABLES:
        schema_editor.execute(
            f"""
            UPDATE {table}
            SET management_queue = CASE
                WHEN regexp_replace(upper(trim(management_queue)), '[^A-Z0-9]+', '_', 'g')
                     IN ({known})
                THEN regexp_replace(upper(trim(management_queue)), '[^A-Z0-9]+', '_', 'g')
                ELSE 'GENERAL'
            END
            """
        )


class Migration(migrations.Migration):
    dependencies = [("maintenance", "0022_remove_workupdate_evidence_delete_workupdateevidence")]

    operations = [
        *[
            migrations.RenameField(
                model_name=model, old_name="department", new_name="management_queue"
            )
            for model in MODELS
        ],
        migrations.RunPython(to_codes, migrations.RunPython.noop),
        *[
            migrations.AlterField(
                model_name=model,
                name="management_queue",
                field=models.CharField(
                    choices=[
                        ("MAINTENANCE", "Maintenance"), ("PLUMBING", "Plumbing"),
                        ("ELECTRICAL", "Electrical"), ("ELEVATOR", "Elevator"),
                        ("HVAC", "HVAC"), ("CLEANING", "Cleaning"),
                        ("SECURITY", "Security"), ("LANDSCAPING", "Landscaping"),
                        ("PEST_CONTROL", "Pest control"), ("GENERAL", "General"),
                    ],
                    max_length=32,
                ),
            )
            for model in MODELS
        ],
    ]
