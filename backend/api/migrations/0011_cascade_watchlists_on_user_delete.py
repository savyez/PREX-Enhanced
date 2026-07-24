from django.db import migrations


class Migration(migrations.Migration):
    """Keep the deployed watchlist constraint aligned with the User model."""

    dependencies = [
        ('api', '0010_cascade_outstanding_tokens_on_user_delete'),
    ]

    operations = [
        migrations.RunSQL(
            sql=(
                'ALTER TABLE "watchlists" '
                'DROP CONSTRAINT IF EXISTS "watchlists_user_id_7f65275a_fk_users_id"; '
                'ALTER TABLE "watchlists" '
                'ADD CONSTRAINT "watchlists_user_id_7f65275a_fk_users_id" '
                'FOREIGN KEY ("user_id") REFERENCES "users" ("id") '
                'ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;'
            ),
            reverse_sql=(
                'ALTER TABLE "watchlists" '
                'DROP CONSTRAINT IF EXISTS "watchlists_user_id_7f65275a_fk_users_id"; '
                'ALTER TABLE "watchlists" '
                'ADD CONSTRAINT "watchlists_user_id_7f65275a_fk_users_id" '
                'FOREIGN KEY ("user_id") REFERENCES "users" ("id") '
                'DEFERRABLE INITIALLY DEFERRED;'
            ),
        ),
    ]
