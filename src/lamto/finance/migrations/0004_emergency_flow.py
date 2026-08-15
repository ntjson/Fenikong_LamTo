import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("finance", "0003_approval_decisions"),
        ("maintenance", "0006_emergency_requests"),
    ]

    operations = [
        migrations.CreateModel(
            name="EmergencyAuthorization",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("reason", models.TextField()),
                ("estimate_vnd", models.BigIntegerField(blank=True, null=True)),
                ("signature", models.CharField(max_length=132)),
                ("authorized_at", models.DateTimeField()),
                ("ratification_deadline", models.DateTimeField()),
                ("drill", models.BooleanField()),
                ("label", models.CharField(max_length=32)),
                ("membership", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="accounts.organizationmembership")),
                ("outbox_event", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="emergency_authorization", to="evidence.blockchainoutboxevent")),
                ("wallet", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="accounts.signerwallet")),
                ("work_order", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="emergency_authorization", to="maintenance.workorder")),
            ],
        ),
        migrations.CreateModel(
            name="EmergencyRatification",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("decision", models.CharField(choices=[("RATIFY", "Ratify"), ("REJECT", "Reject"), ("OVERDUE", "Overdue")], max_length=8)),
                ("outcome", models.CharField(choices=[("RATIFIED", "Ratified"), ("REJECTED", "Rejected"), ("OVERDUE", "Overdue")], max_length=8)),
                ("reason", models.TextField()),
                ("signature", models.CharField(blank=True, max_length=132)),
                ("decided_at", models.DateTimeField()),
                ("label", models.CharField(max_length=32)),
                ("authorization", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="ratification", to="finance.emergencyauthorization")),
                ("membership", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to="accounts.organizationmembership")),
                ("outbox_event", models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="emergency_ratification", to="evidence.blockchainoutboxevent")),
                ("wallet", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to="accounts.signerwallet")),
            ],
        ),
        migrations.AddConstraint(
            model_name="emergencyauthorization",
            constraint=models.CheckConstraint(
                condition=models.Q(estimate_vnd__isnull=True) | models.Q(estimate_vnd__gt=0),
                name="emergency_estimate_positive",
            ),
        ),
        migrations.AddConstraint(
            model_name="emergencyauthorization",
            constraint=models.CheckConstraint(
                condition=models.Q(("ratification_deadline__gt", models.F("authorized_at"))),
                name="emergency_deadline_after_authorization",
            ),
        ),
        migrations.AddConstraint(
            model_name="emergencyratification",
            constraint=models.CheckConstraint(
                condition=(
                    models.Q(
                        decision="OVERDUE", outcome="OVERDUE", membership__isnull=True,
                        wallet__isnull=True, outbox_event__isnull=True, signature=""
                    )
                    | models.Q(
                        decision__in=["RATIFY", "REJECT"], membership__isnull=False,
                        wallet__isnull=False, outbox_event__isnull=False,
                    )
                ),
                name="emergency_ratification_provenance",
            ),
        ),
        migrations.RunSQL(
            sql="""
            CREATE FUNCTION finance_reject_emergency_authorization_mutation()
            RETURNS trigger AS $$
            BEGIN
                RAISE EXCEPTION 'emergency authorizations are immutable'
                USING ERRCODE = 'check_violation';
            END;
            $$ LANGUAGE plpgsql;

            CREATE TRIGGER emergency_authorization_append_only
            BEFORE UPDATE OR DELETE ON finance_emergencyauthorization
            FOR EACH ROW EXECUTE FUNCTION finance_reject_emergency_authorization_mutation();

            CREATE FUNCTION finance_reject_emergency_ratification_mutation()
            RETURNS trigger AS $$
            BEGIN
                RAISE EXCEPTION 'emergency ratifications are immutable'
                USING ERRCODE = 'check_violation';
            END;
            $$ LANGUAGE plpgsql;

            CREATE TRIGGER emergency_ratification_append_only
            BEFORE UPDATE OR DELETE ON finance_emergencyratification
            FOR EACH ROW EXECUTE FUNCTION finance_reject_emergency_ratification_mutation();
            """,
            reverse_sql="""
            DROP TRIGGER emergency_ratification_append_only ON finance_emergencyratification;
            DROP FUNCTION finance_reject_emergency_ratification_mutation();
            DROP TRIGGER emergency_authorization_append_only ON finance_emergencyauthorization;
            DROP FUNCTION finance_reject_emergency_authorization_mutation();
            """,
        ),
    ]
