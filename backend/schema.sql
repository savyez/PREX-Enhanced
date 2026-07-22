-- PREX application schema for PostgreSQL.
--
-- This file documents the tables owned by the api models. The authoritative
-- schema is Django's migration history; run `python manage.py migrate` when
-- creating or updating a database. Django also creates framework tables for
-- permissions, sessions, admin logs, and Simple JWT token blacklisting.

CREATE TABLE users (
    id UUID PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL DEFAULT '',
    last_name VARCHAR(50) NOT NULL DEFAULT '',
    username VARCHAR(150) UNIQUE NOT NULL,
    dob DATE NOT NULL,
    email VARCHAR(254) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email_confirmed BOOLEAN NOT NULL DEFAULT FALSE,
    is_staff BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE coins (
    ticker VARCHAR(16) PRIMARY KEY,
    coin_name VARCHAR(100) UNIQUE NOT NULL,
    price NUMERIC(20, 8) NOT NULL,
    market_cap_rank INTEGER NULL,
    market_volume NUMERIC(24, 2) NOT NULL,
    last_updated_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    price_change_24h NUMERIC(10, 3) NOT NULL DEFAULT 0
);

CREATE TABLE watchlists (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,

    CONSTRAINT fk_watchlists_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT unique_watchlist_name_per_user
        UNIQUE (user_id, name)
);

CREATE INDEX watchlists_user_id_idx ON watchlists(user_id);

CREATE TABLE watchlist_items (
    id BIGSERIAL PRIMARY KEY,
    watchlist_id BIGINT NOT NULL,
    ticker VARCHAR(16) NOT NULL,
    added_at TIMESTAMPTZ NOT NULL,

    CONSTRAINT fk_watchlist_items_watchlist
        FOREIGN KEY (watchlist_id)
        REFERENCES watchlists(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_watchlist_items_coin
        FOREIGN KEY (ticker)
        REFERENCES coins(ticker)
        ON DELETE CASCADE,

    CONSTRAINT unique_coin_per_watchlist
        UNIQUE (watchlist_id, ticker)
);

CREATE INDEX watchlist_items_watchlist_id_idx ON watchlist_items(watchlist_id);
CREATE INDEX watchlist_items_ticker_idx ON watchlist_items(ticker);
