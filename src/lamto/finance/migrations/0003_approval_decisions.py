import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0008_grant_signed_executor"),
        ("evidence", "0007_revoke_legacy_runtime_execute"),
        ("finance", "0002_proposal_integrity"),
    ]

    operations = [
        migrations.CreateModel(
            name="ApprovalDecision",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "stage",
                    models.CharField(
                        choices=[
                            ("BOARD", "Management Board"),
                            ("RESIDENT_REP", "Resident representative"),
                        ],
                        max_length=16,
                    ),
                ),
                (
                    "decision",
                    models.CharField(
                        choices=[("APPROVE", "Approve"), ("REJECT", "Reject")],
                        max_length=8,
                    ),
                ),
                ("reason", models.TextField()),
                ("signature", models.CharField(max_length=132)),
                ("decided_at", models.DateTimeField()),
                (
                    "membership",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="accounts.organizationmembership",
                    ),
                ),
                (
                    "outbox_event",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="approval_decision",
                        to="evidence.blockchainoutboxevent",
                    ),
                ),
                (
                    "version",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="approval_decisions",
                        to="finance.proposalversion",
                    ),
                ),
                (
                    "wallet",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="accounts.signerwallet",
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="approvaldecision",
            constraint=models.UniqueConstraint(
                fields=("version", "stage"), name="approval_decision_once_per_stage"
            ),
        ),
        migrations.RunSQL(
            sql="""
            CREATE FUNCTION finance_reject_approval_mutation()
            RETURNS trigger AS $$
            BEGIN
                RAISE EXCEPTION 'approval decisions are immutable'
                USING ERRCODE = 'check_violation';
            END;
            $$ LANGUAGE plpgsql;

            CREATE TRIGGER approval_decision_append_only
            BEFORE UPDATE OR DELETE ON finance_approvaldecision
            FOR EACH ROW EXECUTE FUNCTION finance_reject_approval_mutation();
            """,
            reverse_sql="""
            DROP TRIGGER approval_decision_append_only ON finance_approvaldecision;
            DROP FUNCTION finance_reject_approval_mutation();
            """,
        ),
    ]
