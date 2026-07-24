from django.db import migrations


class Migration(migrations.Migration):
    """Ensure JWT blacklist rows cannot prevent user deletion."""

    dependencies = [
        ('api', '0009_user_first_name_user_last_name'),
        ('token_blacklist', '0013_alter_blacklistedtoken_options_and_more'),
    ]

    operations = [
        migrations.RunSQL(
            sql=(
                'ALTER TABLE "token_blacklist_outstandingtoken" '
                'DROP CONSTRAINT IF EXISTS "token_blacklist_outstandingtoken_user_id_fkey"; '
                'ALTER TABLE "token_blacklist_outstandingtoken" '
                'ADD CONSTRAINT "token_blacklist_outstandingtoken_user_id_fkey" '
                'FOREIGN KEY ("user_id") REFERENCES "users" ("id") '
                'ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;'
            ),
            reverse_sql=(
                'ALTER TABLE "token_blacklist_outstandingtoken" '
                'DROP CONSTRAINT IF EXISTS "token_blacklist_outstandingtoken_user_id_fkey"; '
                'ALTER TABLE "token_blacklist_outstandingtoken" '
                'ADD CONSTRAINT "token_blacklist_outstandingtoken_user_id_fkey" '
                'FOREIGN KEY ("user_id") REFERENCES "users" ("id") '
                'DEFERRABLE INITIALLY DEFERRED;'
            ),
        ),
    ]
