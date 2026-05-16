import uuid
from django.db import models


# Model for the User, representing a user of the application with their details and authentication information.
class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=150, unique=True)
    dob = models.DateField()
    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=255)
    email_confirmed = models.BooleanField(default=False)
    reset_token = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "users"
        ordering = ["username"]

    def __str__(self):
        return self.username


# Model for the Coin, representing a cryptocurrency with its details.
class Coin(models.Model):
    ticker = models.CharField(max_length=16, primary_key=True)
    coin_name = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=20, decimal_places=8)
    market_volume = models.DecimalField(max_digits=24, decimal_places=2)
    last_updated_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "coins"
        ordering = ["ticker"]

    def __str__(self):
        return f"{self.coin_name} ({self.ticker})"


# Model for the Watchlist, representing a user's collection of coins they want to track.
class Watchlist(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="watchlists")
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "watchlists"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "name"],
                name="unique_watchlist_name_per_user",
            ),
        ]

    def __str__(self):
        return f"{self.name} - {self.user.username}"


# Model for the WatchlistItem, representing the many-to-many relationship between Watchlist and Coin.
class WatchlistItem(models.Model):
    watchlist = models.ForeignKey(Watchlist,on_delete=models.CASCADE,related_name="items")
    ticker = models.ForeignKey(Coin,on_delete=models.CASCADE,db_column="ticker",related_name="watchlist_items")
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "watchlist_items"
        ordering = ["-added_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["watchlist", "ticker"],
                name="unique_coin_per_watchlist",
            ),
        ]

    def __str__(self):
        return f"{self.ticker_id} in {self.watchlist.name}"
