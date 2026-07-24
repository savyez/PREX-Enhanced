from django.db import migrations


class Migration(migrations.Migration):
    """Remove blacklisted-token rows with their outstanding token parent."""

    dependencies = [
        ('api', '0011_cascade_watchlists_on_user_delete'),
        ('token_blacklist', '0013_alter_blacklistedtoken_options_and_more'),
    ]

    operations = [
        migrations.RunSQL(
            sql=(
                'ALTER TABLE "token_blacklist_blacklistedtoken" '
                'DROP CONSTRAINT IF EXISTS '
                '"token_blacklist_blacklistedtoken_token_id_3cc7fe56_fk"; '
                'ALTER TABLE "token_blacklist_blacklistedtoken" '
                'ADD CONSTRAINT '
                '"token_blacklist_blacklistedtoken_token_id_3cc7fe56_fk" '
                'FOREIGN KEY ("token_id") '
                'REFERENCES "token_blacklist_outstandingtoken" ("id") '
                'ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;'
            ),
            reverse_sql=(
                'ALTER TABLE "token_blacklist_blacklistedtoken" '
                'DROP CONSTRAINT IF EXISTS '
                '"token_blacklist_blacklistedtoken_token_id_3cc7fe56_fk"; '
                'ALTER TABLE "token_blacklist_blacklistedtoken" '
                'ADD CONSTRAINT '
                '"token_blacklist_blacklistedtoken_token_id_3cc7fe56_fk" '
                'FOREIGN KEY ("token_id") '
                'REFERENCES "token_blacklist_outstandingtoken" ("id") '
                'DEFERRABLE INITIALLY DEFERRED;'
            ),
        ),
    ]
