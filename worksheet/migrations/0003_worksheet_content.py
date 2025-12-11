from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("worksheet", "0002_config"),
    ]

    operations = [
        migrations.AddField(
            model_name="worksheet",
            name="content",
            field=models.TextField(blank=True, null=True),
        ),
    ]
