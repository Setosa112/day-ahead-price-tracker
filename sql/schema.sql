CREATE TABLE IF NOT EXISTS day_ahead_prices (
    id             SERIAL PRIMARY KEY,
    "timestamp"    TIMESTAMPTZ NOT NULL,
    bidding_zone   TEXT NOT NULL,
    price_eur_mwh  NUMERIC(10, 2) NOT NULL,
    UNIQUE (timestamp, bidding_zone)
);


CREATE TABLE IF NOT EXISTS load_forecast (
    id             SERIAL PRIMARY KEY,
    "timestamp"    TIMESTAMPTZ NOT NULL,
    bidding_zone   TEXT NOT NULL,
    load_mw        NUMERIC(10, 2),
    UNIQUE (timestamp, bidding_zone)
);

CREATE TABLE IF NOT EXISTS generation_forecast (
    id              SERIAL PRIMARY KEY,
    "timestamp"     TIMESTAMPTZ NOT NULL,
    bidding_zone    TEXT NOT NULL,
    source          TEXT NOT NULL,
    generation_mw   NUMERIC(10, 2),
    UNIQUE (timestamp, bidding_zone, source)
);