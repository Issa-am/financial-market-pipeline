WITH source AS (
    SELECT * FROM {{ source('raw_data', 'stocks_raw') }}
),

cleaned AS (
    SELECT
        symbol,
        date::DATE                      AS date,
        open,
        high,
        low,
        close,
        volume,
        ROUND(daily_change, 4)          AS daily_change,
        ROUND(daily_change_pct, 2)      AS daily_change_pct,
        ROUND(price_range, 4)           AS price_range,
        ingested_at::TIMESTAMP          AS ingested_at
    FROM source
    WHERE symbol IS NOT NULL
      AND close > 0
)

SELECT * FROM cleaned