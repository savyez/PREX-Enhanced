from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_alter_user_managers_alter_user_password_hash_and_more'),
        ('token_blacklist', '0013_alter_blacklistedtoken_options_and_more'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                DELETE FROM token_blacklist_outstandingtoken;
                ALTER TABLE token_blacklist_outstandingtoken DROP CONSTRAINT IF EXISTS token_blacklist_outs_user_id_83bc629a_fk_auth_user;
                ALTER TABLE token_blacklist_outstandingtoken ALTER COLUMN user_id DROP NOT NULL;
                ALTER TABLE token_blacklist_outstandingtoken ALTER COLUMN user_id TYPE uuid USING NULL;
                ALTER TABLE token_blacklist_outstandingtoken ADD CONSTRAINT token_blacklist_outstandingtoken_user_id_fkey FOREIGN KEY (user_id) REFERENCES users (id) DEFERRABLE INITIALLY DEFERRED;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
