from django.db import migrations


SQL = """
CREATE OR REPLACE FUNCTION finance_reject_ineligible_publisher()
RETURNS trigger AS $$
DECLARE publisher_user_id bigint; creator_user_id bigint; recorder_user_id bigint;
BEGIN
    SELECT user_id INTO publisher_user_id FROM accounts_managementmembership WHERE id = NEW.publisher_id;
    SELECT creator.user_id INTO creator_user_id
    FROM finance_proposal proposal
    JOIN accounts_managementmembership creator ON creator.id = proposal.creator_membership_id
    WHERE proposal.id = NEW.proposal_id;
    IF publisher_user_id = creator_user_id THEN
        RAISE EXCEPTION 'publisher must differ from proposal creator' USING ERRCODE = 'check_violation';
    END IF;
    SELECT recorder.user_id INTO recorder_user_id
    FROM finance_settlement settlement
    JOIN accounts_managementmembership recorder ON recorder.id = settlement.transfer_recorded_by_id
    WHERE settlement.proposal_id = NEW.proposal_id;
    IF FOUND AND publisher_user_id = recorder_user_id THEN
        RAISE EXCEPTION 'publisher must differ from settlement recorder' USING ERRCODE = 'check_violation';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
"""


class Migration(migrations.Migration):
    dependencies = [("finance", "0020_remove_paymentevidence_acceptance_and_more")]
    operations = [migrations.RunSQL(SQL, migrations.RunSQL.noop)]
