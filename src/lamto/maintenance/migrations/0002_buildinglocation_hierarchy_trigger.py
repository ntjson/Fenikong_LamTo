from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("maintenance", "0001_initial")]

    operations = [
        migrations.RunSQL(
            """
            CREATE FUNCTION maintenance_validate_location_hierarchy()
            RETURNS trigger AS $$
            DECLARE
                parent_building_id bigint;
            BEGIN
                IF NEW.parent_id IS NULL THEN
                    RETURN NEW;
                END IF;
                IF NEW.parent_id = NEW.id THEN
                    RAISE EXCEPTION 'location cannot be its own parent'
                    USING ERRCODE = 'check_violation';
                END IF;
                SELECT building_id INTO parent_building_id
                FROM maintenance_buildinglocation
                WHERE id = NEW.parent_id;
                IF parent_building_id IS NULL OR parent_building_id != NEW.building_id THEN
                    RAISE EXCEPTION 'location parent must belong to the same building'
                    USING ERRCODE = 'check_violation';
                END IF;
                IF EXISTS (
                    WITH RECURSIVE ancestors(id, parent_id, path) AS (
                        SELECT id, parent_id, ARRAY[id]
                        FROM maintenance_buildinglocation
                        WHERE id = NEW.parent_id
                        UNION ALL
                        SELECT location.id, location.parent_id, ancestors.path || location.id
                        FROM maintenance_buildinglocation AS location
                        JOIN ancestors ON location.id = ancestors.parent_id
                        WHERE NOT location.id = ANY(ancestors.path)
                    )
                    SELECT 1 FROM ancestors WHERE id = NEW.id
                ) THEN
                    RAISE EXCEPTION 'location parent cannot create a cycle'
                    USING ERRCODE = 'check_violation';
                END IF;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

            CREATE TRIGGER building_location_hierarchy_valid
            BEFORE INSERT OR UPDATE OF building_id, parent_id ON maintenance_buildinglocation
            FOR EACH ROW EXECUTE FUNCTION maintenance_validate_location_hierarchy();
            """,
            """
            DROP TRIGGER building_location_hierarchy_valid ON maintenance_buildinglocation;
            DROP FUNCTION maintenance_validate_location_hierarchy();
            """,
        )
    ]
