from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('cvapp', '0001_add_user_indexes'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            CREATE UNIQUE INDEX user_email_unique ON auth_user(email);
            """,
            reverse_sql="""
            DROP INDEX IF EXISTS user_email_unique;
            """
        ),
    ]