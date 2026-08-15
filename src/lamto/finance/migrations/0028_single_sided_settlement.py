"""Collapse settlement to a single side: transfer evidence only (ADR 0002).

The payee name, bank reference and the whole acknowledgement side are dropped,
and the two timestamps that only existed to tell the two steps apart collapse
into ``settled_at``. Settlements that had a transfer but never an
acknowledgement keep their transfer time as their settlement time; they carry no
anchor, exactly as before.
"""

from django.db import migrations, models
import django.db.models.deletion


# finance_reject_ineligible_publisher reads the settlement recorder column,
# which this migration renames.
PUBLISHER_TRIGGER = """
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
    JOIN accounts_managementmembership recorder ON recorder.id = settlement.settled_by_id
    WHERE settlement.proposal_id = NEW.proposal_id;
    IF FOUND AND publisher_user_id = recorder_user_id THEN
        RAISE EXCEPTION 'publisher must differ from settlement recorder' USING ERRCODE = 'check_violation';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
"""

PREVIOUS_PUBLISHER_TRIGGER = PUBLISHER_TRIGGER.replace(
    "settlement.settled_by_id", "settlement.transfer_recorded_by_id"
)


class Migration(migrations.Migration):
    dependencies = [("finance", "0027_remove_proposalversion_fund_code")]

    operations = [
        migrations.RemoveConstraint(
            model_name="settlement",
            name="settlement_requires_both_evidence_sides",
        ),
        migrations.RunSQL(
            "UPDATE finance_settlement SET settled_at = transfer_recorded_at WHERE settled_at IS NULL",
            migrations.RunSQL.noop,
        ),
        migrations.RenameField(
            model_name="settlement",
            old_name="transfer_recorded_by",
            new_name="settled_by",
        ),
        migrations.RunSQL(PUBLISHER_TRIGGER, PREVIOUS_PUBLISHER_TRIGGER),
        migrations.AlterField(
            model_name="settlement",
            name="settled_at",
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name="settlement",
            name="settled_by",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="accounts.managementmembership",
            ),
        ),
        migrations.RemoveField(model_name="settlement", name="payee_name"),
        migrations.RemoveField(model_name="settlement", name="bank_reference"),
        migrations.RemoveField(model_name="settlement", name="transfer_recorded_at"),
        migrations.RemoveField(model_name="settlement", name="ack_kind"),
        migrations.RemoveField(model_name="settlement", name="ack"),
        migrations.RemoveField(model_name="settlement", name="ack_recorded_by"),
        migrations.RemoveField(model_name="settlement", name="ack_recorded_at"),
    ]
