-- SQL schema for the cryptocurrency watchlist application.
-- This schema defines the tables for users, coins, watchlists, and watchlist items.

-- The users table stores information about each user, including their username, date of birth, email, 
-- password hash, email confirmation status, and timestamps for when the account was created and last updated.
CREATE TABLE users (
    id UUID PRIMARY KEY,
    username VARCHAR(150) UNIQUE NOT NULL,
    dob DATE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email_confirmed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

-- The coins table stores information about each cryptocurrency, 
-- including its ticker, name, current price, market volume, and timestamps for when it was last updated and created.
CREATE TABLE coins (
    ticker VARCHAR(16) PRIMARY KEY,
    coin_name VARCHAR(100) UNIQUE NOT NULL,
    price NUMERIC(20, 8) NOT NULL,
    market_volume NUMERIC(24, 2) NOT NULL,
    last_updated_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL
);


-- The watchlists table represents a user's collection of coins they want to track. 
--Each watchlist has a unique name per user and is associated with a user through a foreign key.
CREATE TABLE watchlists (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,

    CONSTRAINT fk_watchlists_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT unique_watchlist_name_per_user
        UNIQUE (user_id, name)
);


-- The watchlist_items table represents the many-to-many relationship between watchlists and coins. 
-- Each entry in this table indicates that a specific coin is part of a specific watchlist, along with the timestamp of when it was added. 
--The table includes foreign keys to both the watchlists and coins tables, ensuring referential integrity.
CREATE TABLE watchlist_items (
    id BIGSERIAL PRIMARY KEY,
    watchlist_id BIGINT NOT NULL,
    ticker VARCHAR(16) NOT NULL,
    added_at TIMESTAMP NOT NULL,

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
