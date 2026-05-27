import uuid
from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, username, dob, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        if not username:
            raise ValueError('The Username field must be set')
        if not dob:
            raise ValueError('The date of birth must be set')

        email = self.normalize_email(email)
        user = self.model(
            username=username,
            dob=dob,
            email=email,
            email_confirmed=extra_fields.pop('email_confirmed', False),
            **extra_fields,
        )
        if password is not None:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, username, dob, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, dob, email, password, **extra_fields)


# Model for the User, representing a user of the application with their details and authentication information.
class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=150, unique=True)
    dob = models.DateField()
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255, db_column='password_hash')
    email_confirmed = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'dob']

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
    market_cap_rank = models.IntegerField(null=True, blank=True)
    market_volume = models.DecimalField(max_digits=24, decimal_places=2)
    last_updated_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "coins"
        ordering = ["market_cap_rank"]

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
