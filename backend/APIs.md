# PREX API Reference

Base URL for local development:

```text
http://127.0.0.1:8000/api/v1
```

Replace the host with the deployed API origin in production. All request bodies shown below use JSON and should include:

```http
Content-Type: application/json
```

Protected endpoints additionally require:

```http
Authorization: Bearer <access-token>
```

Error responses generally use this shape:

```json
{
  "error": "Human-readable error message."
}
```

## Status and Public Routes

### `GET /`

Returns a basic API welcome message.

```json
{
  "message": "Welcome to the PREX API!"
}
```

### `GET /health/`

Public health-check endpoint for a load balancer or deployment platform.

```json
{
  "status": "ok",
  "message": "PREX API is healthy and running."
}
```

## Market Data

### `GET /coins/`

Fetches current market data from CoinGecko, updates the local `coins` table, and returns a paginated result.

Query parameters:

| Parameter | Default | Notes |
|---|---:|---|
| `page` | `1` | Values below 1 are changed to 1. |
| `page_size` | `25` | Clamped between 1 and 100. |

Example: `GET /coins/?page=1&page_size=2`

```json
{
  "success": true,
  "page": 1,
  "page_size": 2,
  "total_count": 250,
  "total_pages": 125,
  "results": [
    {
      "ticker": "BTC",
      "coin_name": "Bitcoin",
      "price": "64079.00000000",
      "market_volume": "17988848511.00",
      "last_updated_at": "2026-07-22T15:29:58Z",
      "market_cap_rank": 1,
      "price_change_24h": "1.460"
    }
  ],
  "coins": [
    {
      "ticker": "BTC",
      "coin_name": "Bitcoin",
      "price": "64079.00000000",
      "market_volume": "17988848511.00",
      "last_updated_at": "2026-07-22T15:29:58Z",
      "market_cap_rank": 1,
      "price_change_24h": "1.460"
    }
  ]
}
```

`502` indicates a provider failure or invalid provider response. `504` indicates a CoinGecko timeout.

### `GET /coins/search/<coin_id>/`

Searches locally synchronized coins by ticker or exact coin name.

Example: `GET /coins/search/bitcoin/?page=1&page_size=10`

```json
{
  "success": true,
  "message": "Coins found matching the search query.",
  "page": 1,
  "page_size": 10,
  "total_count": 1,
  "total_pages": 1,
  "results": [
    {
      "ticker": "BTC",
      "coin_name": "Bitcoin",
      "price": "64079.00000000",
      "market_volume": "17988848511.00",
      "last_updated_at": "2026-07-22T15:29:58Z",
      "market_cap_rank": 1,
      "price_change_24h": "1.460"
    }
  ],
  "coins": [
    {
      "ticker": "BTC",
      "coin_name": "Bitcoin",
      "price": "64079.00000000",
      "market_volume": "17988848511.00",
      "last_updated_at": "2026-07-22T15:29:58Z",
      "market_cap_rank": 1,
      "price_change_24h": "1.460"
    }
  ]
}
```

When nothing matches, the endpoint returns `200` with `total_count: 0`, `total_pages: 0`, and an empty `results` array.

### `GET /coins/<coin_id>/chart/`

Resolves a ticker/name through CoinGecko and returns chart points. The default period is seven days.

Query parameter:

| Parameter | Default | Notes |
|---|---:|---|
| `days` | `7` | Invalid values fall back to 7. |

Example: `GET /coins/BTC/chart/?days=7`

```json
{
  "success": true,
  "coin_id": "bitcoin",
  "chart_data": [
    {
      "timestamp": 1784736000000,
      "price": 64079.12
    },
    {
      "timestamp": 1784822400000,
      "price": 64510.44
    }
  ]
}
```

Chart responses are cached for five minutes. Provider timeout and availability responses use `504` and `502` respectively.

## Authentication and Account Routes

### `POST /register/`

Creates an unverified user and sends a verification email.

Request:

```json
{
  "username": "demo_user",
  "dob": "1995-06-10",
  "email": "demo@example.com",
  "password": "A-long-password-123!"
}
```

Response `200`:

```json
{
  "message": "Verification email sent. Verify your email to complete registration."
}
```

The password is validated with Django’s configured password validators. Existing unverified accounts receive a new verification email; existing verified email addresses are rejected.

### `GET /verify/<token>/`

Consumes the signed email-verification token from the email link. On success, the user is activated and the API redirects with `302` to `EMAIL_VERIFICATION_SUCCESS_URL`. Invalid or expired links return an error JSON response.

### `POST /login/`

Authenticates using email and password. The account must have a confirmed email.

Request:

```json
{
  "email": "demo@example.com",
  "password": "A-long-password-123!"
}
```

Response `200`:

```json
{
  "status": 200,
  "success": true,
  "message": "Login Successful, Welcome back demo_user!",
  "access_token": "<access-token>",
  "refresh_token": "<refresh-token>",
  "user": {
    "id": "00000000-0000-0000-0000-000000000001",
    "first_name": "",
    "last_name": "",
    "username": "demo_user",
    "dob": "1995-06-10",
    "email": "demo@example.com",
    "email_confirmed": true
  }
}
```

### `POST /token/refresh/`

Exchanges a valid refresh token for a new access token. Send the refresh token as JSON:

```json
{
  "refresh": "<refresh-token>"
}
```

The response is provided by Simple JWT and contains an `access` token; with rotation enabled it may also contain a new `refresh` token.

### `GET /current-user/`

Requires authentication.

```json
{
  "user": {
    "id": "00000000-0000-0000-0000-000000000001",
    "first_name": "Demo",
    "last_name": "User",
    "username": "demo_user",
    "dob": "1995-06-10",
    "email": "demo@example.com",
    "email_confirmed": true
  }
}
```

### `PATCH /users/<user_id>/`

Requires authentication and the path ID must belong to the authenticated user. Allowed fields are `first_name`, `last_name`, and `username`.

Request:

```json
{
  "first_name": "Demo",
  "last_name": "User",
  "username": "updated_demo_user"
}
```

Response:

```json
{
  "success": true,
  "message": "Profile updated successfully.",
  "user": {
    "id": "00000000-0000-0000-0000-000000000001",
    "first_name": "Demo",
    "last_name": "User",
    "username": "updated_demo_user",
    "dob": "1995-06-10",
    "email": "demo@example.com",
    "email_confirmed": true
  }
}
```

### `POST /reset-password/`

Requests a password-reset email. The response intentionally does not reveal whether an email exists.

Request:

```json
{
  "email": "demo@example.com"
}
```

Response:

```json
{
  "success": true,
  "message": "Password reset instructions sent to demo@example.com."
}
```

For an unknown email, the endpoint returns the generic message `If email exists, reset instructions sent.`.

### `POST /reset-password-confirm/<token>/`

Consumes the signed reset token from the email and changes the password.

Request:

```json
{
  "new_password": "A-new-password-456!",
  "confirm_new_password": "A-new-password-456!"
}
```

Response:

```json
{
  "success": true,
  "message": "Password reset successfully."
}
```

### `POST /logout/`

Requires authentication. The refresh token must belong to the authenticated user; otherwise the API returns `403`. A valid token is blacklisted.

Request:

```json
{
  "refresh_token": "<refresh-token>"
}
```

Response:

```json
{
  "success": true,
  "message": "Logout successful."
}
```

## Watchlist Routes

All watchlist routes require authentication.

### `GET /watchlists/<user_id>/`

The path user ID must match the authenticated user.

```json
{
  "success": true,
  "watchlists": [
    {
      "id": 1,
      "name": "Long Term",
      "created_at": "2026-07-22T10:00:00Z",
      "updated_at": "2026-07-22T10:00:00Z"
    }
  ]
}
```

When no watchlists exist, `watchlists` is empty and a helpful `message` is included.

### `POST /watchlists/create/`

Creates a uniquely named watchlist for the authenticated user. The request only needs the name; ownership comes from the access token.

Request:

```json
{
  "name": "Long Term"
}
```

Response `201`:

```json
{
  "success": true,
  "message": "Watchlist Long Term created successfully.",
  "watchlist": {
    "id": 1,
    "name": "Long Term",
    "created_at": "2026-07-22T10:00:00Z",
    "updated_at": "2026-07-22T10:00:00Z"
  }
}
```

### `POST /watchlists/<watchlist_id>/delete/`

Deletes a watchlist and its items. It requires the authenticated user ID in the request body.

Request:

```json
{
  "user_id": "00000000-0000-0000-0000-000000000001"
}
```

Response:

```json
{
  "success": true,
  "message": "Watchlist Long Term with 1 has been deleted successfully."
}
```

Deleting a watchlist cascades to its watchlist items.

### `POST /watchlists/add-coin/`

Adds a locally synchronized coin to one of the authenticated user’s watchlists.

Request:

```json
{
  "user_id": "00000000-0000-0000-0000-000000000001",
  "watchlist_id": 1,
  "ticker": "BTC"
}
```

Response:

```json
{
  "success": true,
  "message": "Bitcoin (BTC) added to watchlist Long Term.",
  "watchlist": {
    "id": 1,
    "name": "Long Term",
    "created_at": "2026-07-22T10:00:00Z",
    "updated_at": "2026-07-22T10:00:00Z"
  }
}
```

Duplicate membership returns `409`.

### `POST /watchlists/remove-coin/`

Removes a coin from one of the authenticated user’s watchlists.

Request:

```json
{
  "user_id": "00000000-0000-0000-0000-000000000001",
  "watchlist_id": 1,
  "ticker": "BTC"
}
```

Response:

```json
{
  "success": true,
  "message": "Bitcoin (BTC) removed from watchlist Long Term.",
  "watchlist": {
    "id": 1,
    "name": "Long Term",
    "created_at": "2026-07-22T10:00:00Z",
    "updated_at": "2026-07-22T10:00:00Z"
  }
}
```

### `GET /watchlists/<watchlist_id>/items/`

Returns the watchlist’s coins. The authenticated user must own the watchlist.

```json
{
  "success": true,
  "watchlist": "Long Term",
  "items": [
    {
      "id": 1,
      "ticker": {
        "ticker": "BTC",
        "coin_name": "Bitcoin",
        "price": "64079.00000000",
        "market_volume": "17988848511.00",
        "last_updated_at": "2026-07-22T15:29:58Z",
        "market_cap_rank": 1,
        "price_change_24h": "1.460"
      },
      "added_at": "2026-07-22T10:05:00Z"
    }
  ]
}
```

### `GET /watchlists/membership/<ticker>/`

Returns every watchlist owned by the authenticated user that contains the ticker.

```json
{
  "success": true,
  "membership": [
    {
      "item_id": 1,
      "watchlist_id": 1,
      "watchlist_name": "Long Term",
      "added_at": "2026-07-22T10:05:00Z"
    }
  ]
}
```

An existing coin with no memberships returns an empty array. Unknown tickers return `404`.

## Common Errors

| Status | Meaning |
|---:|---|
| `400` | Missing/invalid request data or expired/tampered signed link |
| `401` | Missing, invalid or expired access token |
| `403` | Authenticated user is not allowed to access the requested resource |
| `404` | User, watchlist, coin or requested data was not found |
| `409` | Duplicate username/watchlist/membership conflict |
| `502` | External CoinGecko or SMTP provider failure |
| `504` | External CoinGecko request timed out |

## Postman

`PREX.postman_collection.json` contains local request examples for the main authentication, market-data and watchlist flows. Replace any saved bearer tokens, user IDs, hostnames and request values before use. Never share real access or refresh tokens.
