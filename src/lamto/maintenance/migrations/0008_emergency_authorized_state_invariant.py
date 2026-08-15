from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("maintenance", "0007_emergency_authorization_boundary"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            CREATE OR REPLACE FUNCTION maintenance_require_emergency_authorization()
            RETURNS trigger AS $$
            BEGIN
                -- State invariant: emergency + AUTHORIZED always requires EA row.
                IF NEW.emergency IS TRUE AND NEW.authorization_status = 'AUTHORIZED' THEN
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
            """,
            reverse_sql="""
            CREATE OR REPLACE FUNCTION maintenance_require_emergency_authorization()
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
            """,
        ),
    ]
