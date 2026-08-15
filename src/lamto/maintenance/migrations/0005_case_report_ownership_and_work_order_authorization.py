from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("maintenance", "0004_cases_and_workorders")]

    operations = [
        migrations.AddConstraint(
            model_name="workorder",
            constraint=models.CheckConstraint(
                condition=(
                    models.Q(requires_spending=False, authorization_status="NOT_REQUIRED")
                    | models.Q(requires_spending=True, authorization_status__in=["PENDING", "AUTHORIZED"])
                ),
                name="work_order_spending_authorization",
            ),
        ),
        migrations.RunSQL(
            """
            CREATE FUNCTION maintenance_case_report_active_owner()
            RETURNS trigger AS $$
            BEGIN
                PERFORM pg_advisory_xact_lock(NEW.report_id);
                IF EXISTS (
                    SELECT 1
                    FROM maintenance_casereport AS link
                    JOIN maintenance_maintenancecase AS active_case ON active_case.id = link.case_id
                    WHERE link.report_id = NEW.report_id
                      AND active_case.active
                      AND link.case_id <> NEW.case_id
                ) THEN
                    RAISE EXCEPTION 'report already belongs to another active case'
                    USING ERRCODE = 'check_violation';
                END IF;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

            CREATE TRIGGER case_report_one_active_case
            BEFORE INSERT OR UPDATE OF case_id, report_id ON maintenance_casereport
            FOR EACH ROW EXECUTE FUNCTION maintenance_case_report_active_owner();

            CREATE FUNCTION maintenance_case_reactivation_active_owner()
            RETURNS trigger AS $$
            DECLARE
                linked_report_id bigint;
            BEGIN
                IF NOT OLD.active AND NEW.active THEN
                    FOR linked_report_id IN
                        SELECT report_id
                        FROM maintenance_casereport
                        WHERE case_id = NEW.id
                        ORDER BY report_id
                    LOOP
                        PERFORM pg_advisory_xact_lock(linked_report_id);
                        IF EXISTS (
                            SELECT 1
                            FROM maintenance_casereport AS link
                            JOIN maintenance_maintenancecase AS active_case ON active_case.id = link.case_id
                            WHERE link.report_id = linked_report_id
                              AND active_case.active
                              AND link.case_id <> NEW.id
                        ) THEN
                            RAISE EXCEPTION 'report already belongs to another active case'
                            USING ERRCODE = 'check_violation';
                        END IF;
                    END LOOP;
                END IF;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

            CREATE TRIGGER maintenance_case_reactivation_one_active_case
            BEFORE UPDATE OF active ON maintenance_maintenancecase
            FOR EACH ROW EXECUTE FUNCTION maintenance_case_reactivation_active_owner();
            """,
            """
            DROP TRIGGER maintenance_case_reactivation_one_active_case ON maintenance_maintenancecase;
            DROP FUNCTION maintenance_case_reactivation_active_owner();
            DROP TRIGGER case_report_one_active_case ON maintenance_casereport;
            DROP FUNCTION maintenance_case_report_active_owner();
            """,
        ),
    ]
