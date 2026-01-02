from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("worksheet", "0003_worksheet_content"),
    ]

    operations = [
        migrations.AddField(
            model_name="worksheet",
            name="themes",
            field=models.JSONField(blank=True, null=True),
        ),
    ]
