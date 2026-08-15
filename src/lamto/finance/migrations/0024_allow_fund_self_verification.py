from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("finance", "0023_remove_proposalversion_creator_wallet")]
    operations = [
        migrations.RunSQL(
            """
            DROP TRIGGER IF EXISTS fund_verification_maker_checker ON finance_fundentryverification;
            DROP FUNCTION IF EXISTS finance_reject_fund_self_verification();
            """,
            migrations.RunSQL.noop,
        ),
    ]
