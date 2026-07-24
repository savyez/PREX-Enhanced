from django.db import migrations


class Migration(migrations.Migration):
    """Remove watchlist items with their deleted watchlist parent."""

    dependencies = [
        ('api', '0012_cascade_blacklisted_tokens_on_outstanding_delete'),
    ]

    operations = [
        migrations.RunSQL(
            sql=(
                'ALTER TABLE "watchlist_items" '
                'DROP CONSTRAINT IF EXISTS '
                '"watchlist_items_watchlist_id_e6772bf2_fk_watchlists_id"; '
                'ALTER TABLE "watchlist_items" '
                'ADD CONSTRAINT '
                '"watchlist_items_watchlist_id_e6772bf2_fk_watchlists_id" '
                'FOREIGN KEY ("watchlist_id") REFERENCES "watchlists" ("id") '
                'ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;'
            ),
            reverse_sql=(
                'ALTER TABLE "watchlist_items" '
                'DROP CONSTRAINT IF EXISTS '
                '"watchlist_items_watchlist_id_e6772bf2_fk_watchlists_id"; '
                'ALTER TABLE "watchlist_items" '
                'ADD CONSTRAINT '
                '"watchlist_items_watchlist_id_e6772bf2_fk_watchlists_id" '
                'FOREIGN KEY ("watchlist_id") REFERENCES "watchlists" ("id") '
                'DEFERRABLE INITIALLY DEFERRED;'
            ),
        ),
    ]
