from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("evidence", "0017_alter_blockchainoutboxevent_event_type")]
    operations = [
        migrations.AlterField(
            model_name="blockchainoutboxevent",
            name="event_type",
            field=models.PositiveSmallIntegerField(choices=[(1, "Proposal created"), (2, "Reserved"), (3, "Reserved"), (4, "Reserved"), (5, "Reserved"), (10, "Settlement")]),
        ),
    ]
