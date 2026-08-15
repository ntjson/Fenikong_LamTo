from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("gate", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="PhotoDeletion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("storage_key", models.CharField(max_length=512, unique=True)),
                ("provider_version_id", models.CharField(blank=True, max_length=512)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
