from django.db import migrations


class Migration(migrations.Migration):
    """Drop the table left behind by the removed `recipients` app.

    Worksheet emails now go to a Mailgun mailing list instead.
    """

    dependencies = [
        ("users", "0002_user_date_joined_user_groups_user_is_staff_and_more"),
    ]

    operations = [
        migrations.RunSQL(
            "DROP TABLE IF EXISTS recipients_userrecipient;",
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
