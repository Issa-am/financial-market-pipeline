-- fct_stocks.sql
-- Facts model: aggregates stock data for analytics
-- Builds on top of stg_stocks staging model

WITH staged AS (
    SELECT * FROM {{ ref('stg_stocks') }}
),

aggregated AS (
    SELECT
        symbol,
        MIN(date)                           AS first_date,
        MAX(date)                           AS last_date,
        COUNT(*)                            AS trading_days,
        ROUND(AVG(close), 2)               AS avg_close_price,
        ROUND(MIN(close), 2)               AS min_close_price,
        ROUND(MAX(close), 2)               AS max_close_price,
        ROUND(AVG(volume), 0)              AS avg_daily_volume,
        ROUND(AVG(daily_change_pct), 2)    AS avg_daily_change_pct,
        ROUND(MAX(daily_change_pct), 2)    AS best_day_pct,
        ROUND(MIN(daily_change_pct), 2)    AS worst_day_pct,
        ROUND(AVG(price_range), 2)         AS avg_daily_range
    FROM staged
    GROUP BY symbol
)

SELECT * FROM aggregated
ORDER BY symbol