from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("finance", "0001_initial")]

    operations = [
        migrations.RunSQL(
            sql="""
            CREATE OR REPLACE FUNCTION finance_reject_proposal_mutation()
            RETURNS trigger AS $$
            BEGIN
                RAISE EXCEPTION 'proposal history is immutable'
                USING ERRCODE = 'check_violation';
            END;
            $$ LANGUAGE plpgsql;

            DROP TRIGGER IF EXISTS proposal_version_append_only ON finance_proposalversion;
            CREATE TRIGGER proposal_version_append_only
            BEFORE UPDATE OR DELETE ON finance_proposalversion
            FOR EACH ROW EXECUTE FUNCTION finance_reject_proposal_mutation();

            DROP TRIGGER IF EXISTS proposal_document_append_only ON finance_proposaldocument;
            CREATE TRIGGER proposal_document_append_only
            BEFORE UPDATE OR DELETE ON finance_proposaldocument
            FOR EACH ROW EXECUTE FUNCTION finance_reject_proposal_mutation();

            CREATE OR REPLACE FUNCTION finance_protect_proposal_mode()
            RETURNS trigger AS $$
            BEGIN
                IF OLD.mode IS DISTINCT FROM NEW.mode THEN
                    RAISE EXCEPTION 'proposal mode is immutable'
                    USING ERRCODE = 'check_violation';
                END IF;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

            DROP TRIGGER IF EXISTS proposal_mode_immutable ON finance_proposal;
            CREATE TRIGGER proposal_mode_immutable
            BEFORE UPDATE ON finance_proposal
            FOR EACH ROW EXECUTE FUNCTION finance_protect_proposal_mode();
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
