from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("maintenance", "0002_buildinglocation_hierarchy_trigger")]

    operations = [
        migrations.RunSQL(
            """
            CREATE FUNCTION maintenance_reject_location_building_change()
            RETURNS trigger AS $$
            BEGIN
                IF NEW.building_id IS DISTINCT FROM OLD.building_id
                   AND EXISTS (
                       SELECT 1
                       FROM maintenance_buildinglocation
                       WHERE parent_id = OLD.id
                   ) THEN
                    RAISE EXCEPTION 'location building cannot change while it has descendants'
                    USING ERRCODE = 'check_violation';
                END IF;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

            CREATE TRIGGER building_location_building_immutable_for_children
            BEFORE UPDATE OF building_id ON maintenance_buildinglocation
            FOR EACH ROW EXECUTE FUNCTION maintenance_reject_location_building_change();
            """,
            """
            DROP TRIGGER building_location_building_immutable_for_children
            ON maintenance_buildinglocation;
            DROP FUNCTION maintenance_reject_location_building_change();
            """,
        )
    ]
