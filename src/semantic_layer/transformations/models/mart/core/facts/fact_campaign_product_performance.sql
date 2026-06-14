{{ config(materialized='table') }}

WITH campaigns AS (

    SELECT *
    FROM {{ ref('dim_campaigns') }}

),

products AS (

    SELECT
        product_id,
        product_sku,
        name AS product_name,
        price
    FROM {{ ref('dim_products') }}
    WHERE is_current = true

),

order_items AS (

    SELECT
        order_id,
        product_id,
        quantity,
        price
    FROM {{ ref('stg_order_items') }}

),

orders AS (

    SELECT
        order_id,
        order_date,
        branch_country,
        branch_city,
        status
    FROM {{ ref('fact_orders') }}
    WHERE status = 'paid'

),

campaign_orders AS (

    SELECT
        c.campaign_id,
        c.platform,
        c.product_sku,
        c.campaign_name,
        c.owner,
        c.start_date,
        c.end_date,
        c.status                        AS campaign_status,
        c.budget_eur,
        c.spend_eur,
        c.revenue_eur                   AS campaign_reported_revenue_eur,
        c.impressions,
        c.clicks,
        c.conversions,
        c.ctr_pct,
        c.roas,
        c.cpc_eur,

        p.product_name,
        p.price                         AS product_price,

        COUNT(DISTINCT o.order_id)      AS orders_during_campaign,
        SUM(oi.quantity)                AS units_sold_during_campaign,
        SUM(oi.quantity * oi.price)     AS actual_revenue_eur_during_campaign

    FROM campaigns c

    LEFT JOIN products p
        ON c.product_sku = p.product_sku

    LEFT JOIN order_items oi
        ON oi.product_id = p.product_id

    LEFT JOIN orders o
        ON oi.order_id = o.order_id
        AND o.order_date BETWEEN c.start_date AND c.end_date

    GROUP BY
        c.campaign_id,
        c.platform,
        c.product_sku,
        c.campaign_name,
        c.owner,
        c.start_date,
        c.end_date,
        c.status,
        c.budget_eur,
        c.spend_eur,
        c.revenue_eur,
        c.impressions,
        c.clicks,
        c.conversions,
        c.ctr_pct,
        c.roas,
        c.cpc_eur,
        p.product_name,
        p.price

)

SELECT

    campaign_id,
    platform,
    product_sku,
    product_name,
    product_price,
    campaign_name,
    owner,
    start_date,
    end_date,
    campaign_status,

    -- Campaign reported metrics
    budget_eur,
    spend_eur,
    campaign_reported_revenue_eur,
    impressions,
    clicks,
    conversions,
    ctr_pct,
    roas,
    cpc_eur,

    -- Observed order metrics during campaign window
    orders_during_campaign,
    units_sold_during_campaign,
    actual_revenue_eur_during_campaign,

    -- Delta: reported vs observed
    ROUND(
        actual_revenue_eur_during_campaign - campaign_reported_revenue_eur,
        2
    ) AS revenue_delta_eur

FROM campaign_orders
