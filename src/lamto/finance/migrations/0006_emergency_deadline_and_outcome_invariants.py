from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("finance", "0005_remove_emergencyratification_emergency_ratification_provenance_and_more"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RemoveConstraint(
                    model_name="emergencyauthorization",
                    name="emergency_deadline_after_authorization",
                ),
                migrations.AddConstraint(
                    model_name="emergencyauthorization",
                    constraint=models.CheckConstraint(
                        condition=models.Q(
                            ratification_deadline__gt=models.F("authorized_at")
                        ),
                        name="emergency_deadline_exact_24h",
                    ),
                ),
            ],
            database_operations=[
                migrations.RunSQL(
                    sql="""
                    ALTER TABLE finance_emergencyauthorization
                        DROP CONSTRAINT IF EXISTS emergency_deadline_after_authorization;
                    ALTER TABLE finance_emergencyauthorization
                        ADD CONSTRAINT emergency_deadline_exact_24h
                        CHECK (ratification_deadline = authorized_at + interval '24 hours');

                    CREATE FUNCTION finance_validate_emergency_outcome_time()
                    RETURNS trigger AS $$
                    DECLARE
                        deadline timestamptz;
                    BEGIN
                        SELECT ratification_deadline INTO deadline
                        FROM finance_emergencyauthorization
                        WHERE id = NEW.authorization_id;
                        IF NOT FOUND THEN
                            RAISE EXCEPTION 'emergency authorization missing for outcome'
                            USING ERRCODE = 'foreign_key_violation';
                        END IF;
                        IF NEW.decision = 'OVERDUE' AND NEW.decided_at < deadline THEN
                            RAISE EXCEPTION 'overdue outcome before ratification deadline'
                            USING ERRCODE = 'check_violation';
                        END IF;
                        IF NEW.decision IN ('RATIFY', 'REJECT')
                           AND NEW.decided_at >= deadline THEN
                            RAISE EXCEPTION 'human emergency outcome at or after deadline'
                            USING ERRCODE = 'check_violation';
                        END IF;
                        RETURN NEW;
                    END;
                    $$ LANGUAGE plpgsql;

                    CREATE TRIGGER emergency_ratification_time_valid
                    BEFORE INSERT ON finance_emergencyratification
                    FOR EACH ROW EXECUTE FUNCTION finance_validate_emergency_outcome_time();
                    """,
                    reverse_sql="""
                    DROP TRIGGER IF EXISTS emergency_ratification_time_valid
                        ON finance_emergencyratification;
                    DROP FUNCTION IF EXISTS finance_validate_emergency_outcome_time();
                    ALTER TABLE finance_emergencyauthorization
                        DROP CONSTRAINT IF EXISTS emergency_deadline_exact_24h;
                    ALTER TABLE finance_emergencyauthorization
                        ADD CONSTRAINT emergency_deadline_after_authorization
                        CHECK (ratification_deadline > authorized_at);
                    """,
                ),
            ],
        ),
    ]
