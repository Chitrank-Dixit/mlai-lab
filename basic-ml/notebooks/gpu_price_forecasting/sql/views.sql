-- PostgreSQL Analytical Views for GPU Price Forecasting

-- View 1: Latest GPU Effective Prices per SKU & Retailer
CREATE OR REPLACE VIEW v_latest_gpu_prices AS
WITH ranked_obs AS (
    SELECT 
        d.observation_id,
        l.sku_id,
        p.model_name,
        p.chipset,
        p.vram_gb,
        p.msrp_inr,
        r.retailer_name,
        d.date,
        d.price_inr,
        d.shipping_cost_inr,
        (d.price_inr + d.shipping_cost_inr) AS total_effective_price_inr,
        ROUND((d.price_inr + d.shipping_cost_inr) / p.msrp_inr, 4) AS msrp_premium_ratio,
        d.in_stock,
        d.is_local_quote,
        ROW_NUMBER() OVER (PARTITION BY l.sku_id, l.retailer_id ORDER BY d.date DESC) AS rn
    FROM daily_price_observations d
    JOIN product_listings l ON d.listing_id = l.listing_id
    JOIN products p ON l.sku_id = p.sku_id
    JOIN retailers r ON l.retailer_id = r.retailer_id
)
SELECT 
    sku_id,
    model_name,
    chipset,
    vram_gb,
    msrp_inr,
    retailer_name,
    date AS latest_observation_date,
    price_inr,
    shipping_cost_inr,
    total_effective_price_inr,
    msrp_premium_ratio,
    in_stock,
    is_local_quote
FROM ranked_obs
WHERE rn = 1;

-- View 2: Daily Minimum Effective Price per SKU across all retailers
CREATE OR REPLACE VIEW v_sku_daily_min_price AS
SELECT 
    l.sku_id,
    p.chipset,
    p.vram_gb,
    d.date,
    MIN(d.price_inr + d.shipping_cost_inr) AS min_effective_price_inr,
    AVG(d.price_inr + d.shipping_cost_inr) AS avg_effective_price_inr
FROM daily_price_observations d
JOIN product_listings l ON d.listing_id = l.listing_id
JOIN products p ON l.sku_id = p.sku_id
WHERE d.in_stock = TRUE
GROUP BY l.sku_id, p.chipset, p.vram_gb, d.date;
