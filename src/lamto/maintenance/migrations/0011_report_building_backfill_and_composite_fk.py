from django.db import migrations


def backfill_report_building(apps, schema_editor):
    # No joined-field updates in Django's .update(); loop instead (small table).
    IssueReport = apps.get_model("maintenance", "IssueReport")
    for report in (
        IssueReport.objects.select_related("unit")
        .filter(building__isnull=True)
        .iterator()
    ):
        report.building_id = report.unit.building_id
        report.save(update_fields=["building"])


COMPOSITE_FKS = """
ALTER TABLE maintenance_maintenancecase
    ADD CONSTRAINT case_location_same_building
    FOREIGN KEY (location_id, building_id)
    REFERENCES maintenance_buildinglocation (id, building_id);
ALTER TABLE maintenance_issuereport
    ADD CONSTRAINT report_unit_same_building
    FOREIGN KEY (unit_id, building_id)
    REFERENCES accounts_unit (id, building_id);
ALTER TABLE maintenance_issuereport
    ADD CONSTRAINT report_location_same_building
    FOREIGN KEY (selected_location_id, building_id)
    REFERENCES maintenance_buildinglocation (id, building_id);
"""

DROP_COMPOSITE_FKS = """
ALTER TABLE maintenance_issuereport DROP CONSTRAINT report_location_same_building;
ALTER TABLE maintenance_issuereport DROP CONSTRAINT report_unit_same_building;
ALTER TABLE maintenance_maintenancecase DROP CONSTRAINT case_location_same_building;
"""


class Migration(migrations.Migration):
    dependencies = [
        ("maintenance", "0010_issuereport_building_and_more"),
        ("accounts", "0011_unit_unit_id_building_key"),
    ]

    operations = [
        migrations.RunPython(backfill_report_building, migrations.RunPython.noop),
        migrations.RunSQL(COMPOSITE_FKS, DROP_COMPOSITE_FKS),
    ]
