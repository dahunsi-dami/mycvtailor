# Generated by Django 5.1.3 on 2024-11-21 17:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            CREATE INDEX IF NOT EXISTS auth_user_id_idx ON auth_user(id);
            CREATE INDEX IF NOT EXISTS auth_user_username_idx ON auth_user(username);
            CREATE INDEX IF NOT EXISTS auth_user_email_idx ON auth_user(email);
            """,
            reverse_sql="""
            DROP INDEX IF EXISTS auth_user_id_idx;
            DROP INDEX IF EXISTS auth_user_username_idx;
            DROP INDEX IF EXISTS auth_user_email_idx;
            """
        ),
    ]