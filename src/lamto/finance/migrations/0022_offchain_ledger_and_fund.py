from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("finance", "0021_update_publication_publisher_trigger")]
    operations = [
        migrations.RunSQL(
            """
            DROP TRIGGER IF EXISTS publication_snapshot_publisher_dual_control ON finance_publicationsnapshot;
            DROP TRIGGER IF EXISTS publication_snapshot_append_only ON finance_publicationsnapshot;
            DROP FUNCTION IF EXISTS finance_reject_publication_snapshot_mutation();
            DROP TRIGGER IF EXISTS publication_gate_failure_append_only ON finance_publicationgatefailure;
            DROP FUNCTION IF EXISTS finance_reject_publication_gate_failure_mutation();
            """,
            migrations.RunSQL.noop,
        ),
        migrations.RemoveField("publishedledgerentry", "snapshot"),
        migrations.RenameField("publishedledgerentry", "payment", "settlement"),
        migrations.AlterField("publishedledgerentry", "settlement", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="ledger_entry", to="finance.settlement")),
        migrations.AddField("publishedledgerentry", "resident_payload", models.JSONField(default=dict)),
        migrations.AlterField("publishedledgerentry", "case", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to="maintenance.maintenancecase")),
        migrations.RemoveField("maintenancefundentry", "publication"),
        migrations.RemoveField("maintenancefundentry", "wallet"),
        migrations.RemoveField("maintenancefundentry", "outbox_event"),
        migrations.RemoveField("maintenancefundentry", "signature"),
        migrations.RemoveField("fundentryverification", "wallet"),
        migrations.RemoveField("fundentryverification", "outbox_event"),
        migrations.RemoveField("fundentryverification", "signature"),
        migrations.DeleteModel("PublicationGateFailure"),
        migrations.DeleteModel("PublicationSnapshot"),
    ]
