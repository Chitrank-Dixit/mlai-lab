-- PostgreSQL Schema DDL for GPU Price Forecasting Workspace

CREATE TABLE IF NOT EXISTS products (
    sku_id VARCHAR(64) PRIMARY KEY,
    gpu_series VARCHAR(64) NOT NULL,
    chipset VARCHAR(64) NOT NULL,
    brand VARCHAR(64) NOT NULL,
    model_name VARCHAR(128) NOT NULL,
    vram_gb INTEGER NOT NULL,
    vram_type VARCHAR(32) NOT NULL,
    msrp_inr NUMERIC(10, 2) NOT NULL,
    is_reference_spec BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS retailers (
    retailer_id VARCHAR(64) PRIMARY KEY,
    retailer_name VARCHAR(128) NOT NULL,
    retailer_type VARCHAR(32) NOT NULL,
    region VARCHAR(32) DEFAULT 'India',
    currency VARCHAR(10) DEFAULT 'INR',
    trust_score NUMERIC(3, 2) DEFAULT 0.90,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS product_listings (
    listing_id VARCHAR(64) PRIMARY KEY,
    sku_id VARCHAR(64) REFERENCES products(sku_id),
    retailer_id VARCHAR(64) REFERENCES retailers(retailer_id),
    listing_title VARCHAR(255) NOT NULL,
    url_or_ref TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS daily_price_observations (
    observation_id VARCHAR(64) PRIMARY KEY,
    listing_id VARCHAR(64) REFERENCES product_listings(listing_id),
    date DATE NOT NULL,
    price_inr NUMERIC(10, 2) NOT NULL,
    in_stock BOOLEAN DEFAULT TRUE,
    shipping_cost_inr NUMERIC(8, 2) DEFAULT 0,
    is_local_quote BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS external_market_signals (
    date DATE PRIMARY KEY,
    usd_inr_rate NUMERIC(8, 4),
    crypto_mining_index NUMERIC(8, 2),
    silicon_supply_index NUMERIC(8, 2),
    import_duty_rate NUMERIC(4, 2)
);

CREATE INDEX IF NOT EXISTS idx_obs_listing_date ON daily_price_observations(listing_id, date);
