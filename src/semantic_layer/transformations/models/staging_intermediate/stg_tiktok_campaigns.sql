{{ config(materialized='table') }}

WITH source_data AS (
    SELECT *
    FROM {{ source('raw', 'tiktok_campaigns') }}
),

cleaned AS (
    SELECT
        campaign_id,
        campaign_name,
        platform,
        owner,
        product_sku,
        CAST(start_date AS DATE)     AS start_date,
        CAST(end_date AS DATE)       AS end_date,
        CAST(budget_eur AS DOUBLE)   AS budget_eur,
        CAST(impressions AS BIGINT)  AS impressions,
        CAST(clicks AS BIGINT)       AS clicks,
        CAST(conversions AS BIGINT)  AS conversions,
        CAST(spend_eur AS DOUBLE)    AS spend_eur,
        CAST(revenue_eur AS DOUBLE)  AS revenue_eur,
        LOWER(status)                AS status,
        CURRENT_TIMESTAMP            AS dbt_loaded_at,
        '{{ invocation_id }}'        AS dbt_run_id,
        to_hex(md5(to_utf8(concat_ws('|',
            campaign_id,
            coalesce(status, ''),
            CAST(spend_eur AS VARCHAR),
            CAST(revenue_eur AS VARCHAR)
        )))) AS row_hash
    FROM source_data
),

deduplicated AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY campaign_id
            ORDER BY end_date DESC NULLS LAST
        ) AS rn
    FROM cleaned
)

SELECT
    campaign_id,
    campaign_name,
    platform,
    owner,
    product_sku,
    start_date,
    end_date,
    budget_eur,
    impressions,
    clicks,
    conversions,
    spend_eur,
    revenue_eur,
    status,
    dbt_loaded_at,
    row_hash,
    dbt_run_id
FROM deduplicated
WHERE rn = 1
