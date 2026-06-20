{{ config(materialized='table') }}

WITH campaigns AS (

    SELECT *
    FROM {{ ref('int_campaigns') }}

)

SELECT

    campaign_id,

    campaign_name,
    platform,
    owner,
    product_sku,
    start_date,
    end_date,
    status,
    budget_eur,

    -- Budget & spend
    spend_eur,
    revenue_eur,
    impressions,

    -- Engagement
    clicks,
    conversions,
    dbt_loaded_at,

    -- Computed KPIs
    row_hash,

    dbt_run_id,

    ROW_NUMBER() OVER (ORDER BY platform, campaign_id) AS campaign_sk,

    CASE
        WHEN impressions > 0
            THEN ROUND(CAST(clicks AS DOUBLE) / impressions * 100, 2)
        ELSE 0
    END AS ctr_pct,
    CASE
        WHEN spend_eur > 0
            THEN ROUND(CAST(revenue_eur AS DOUBLE) / spend_eur, 2)
        ELSE 0
    END AS roas,
    CASE
        WHEN clicks > 0
            THEN ROUND(CAST(spend_eur AS DOUBLE) / clicks, 2)
        ELSE 0
    END AS cpc_eur

FROM campaigns
