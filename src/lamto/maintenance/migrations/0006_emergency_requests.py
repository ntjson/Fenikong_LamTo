import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0008_grant_signed_executor"),
        ("maintenance", "0005_case_report_ownership_and_work_order_authorization"),
    ]

    operations = [
        migrations.AddField(
            model_name="workorder",
            name="emergency_requested_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="workorder",
            name="emergency_requested_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="accounts.organizationmembership",
            ),
        ),
        migrations.AddField(
            model_name="workorder",
            name="emergency_reason",
            field=models.TextField(blank=True),
        ),
        migrations.RunSQL(
            sql="""
            CREATE FUNCTION maintenance_reject_emergency_request_mutation()
            RETURNS trigger AS $$
            BEGIN
                IF OLD.emergency_requested_at IS NOT NULL AND (
                    NEW.emergency IS DISTINCT FROM TRUE
                    OR NEW.drill IS DISTINCT FROM OLD.drill
                    OR NEW.emergency_requested_by_id IS DISTINCT FROM OLD.emergency_requested_by_id
                    OR NEW.emergency_reason IS DISTINCT FROM OLD.emergency_reason
                    OR NEW.emergency_requested_at IS DISTINCT FROM OLD.emergency_requested_at
                ) THEN
                    RAISE EXCEPTION 'emergency request identity is immutable'
                    USING ERRCODE = 'check_violation';
                END IF;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

            CREATE TRIGGER work_order_emergency_request_immutable
            BEFORE UPDATE OF emergency, drill, emergency_requested_by_id, emergency_reason, emergency_requested_at
            ON maintenance_workorder
            FOR EACH ROW EXECUTE FUNCTION maintenance_reject_emergency_request_mutation();
            """,
            reverse_sql="""
            DROP TRIGGER work_order_emergency_request_immutable ON maintenance_workorder;
            DROP FUNCTION maintenance_reject_emergency_request_mutation();
            """,
        ),
    ]
