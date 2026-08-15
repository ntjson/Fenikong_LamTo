from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("maintenance", "0006_emergency_requests"),
        ("finance", "0004_emergency_flow"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="workorder",
            constraint=models.CheckConstraint(
                condition=(
                    models.Q(
                        emergency=False,
                        emergency_requested_at__isnull=True,
                        emergency_requested_by__isnull=True,
                        emergency_reason="",
                    )
                    | (
                        models.Q(emergency=True)
                        & models.Q(emergency_requested_at__isnull=False)
                        & models.Q(emergency_requested_by__isnull=False)
                        & ~models.Q(emergency_reason="")
                    )
                ),
                name="work_order_emergency_request_identity",
            ),
        ),
        migrations.RunSQL(
            sql="""
            CREATE FUNCTION maintenance_require_emergency_authorization()
            RETURNS trigger AS $$
            BEGIN
                IF NEW.emergency IS TRUE
                   AND NEW.authorization_status = 'AUTHORIZED'
                   AND (
                        TG_OP = 'INSERT'
                        OR OLD.authorization_status IS DISTINCT FROM 'AUTHORIZED'
                   )
                THEN
                    IF NOT EXISTS (
                        SELECT 1
                        FROM finance_emergencyauthorization ea
                        WHERE ea.work_order_id = NEW.id
                    ) THEN
                        RAISE EXCEPTION
                            'emergency work order requires emergency authorization'
                            USING ERRCODE = 'check_violation';
                    END IF;
                END IF;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

            CREATE TRIGGER work_order_emergency_authorization_required
            BEFORE INSERT OR UPDATE OF authorization_status, emergency
            ON maintenance_workorder
            FOR EACH ROW EXECUTE FUNCTION maintenance_require_emergency_authorization();
            """,
            reverse_sql="""
            DROP TRIGGER IF EXISTS work_order_emergency_authorization_required
                ON maintenance_workorder;
            DROP FUNCTION IF EXISTS maintenance_require_emergency_authorization();
            """,
        ),
    ]
