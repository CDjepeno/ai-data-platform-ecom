{{ config(materialized='table') }}

WITH order_items AS (

    SELECT *
    FROM {{ ref('stg_order_items') }}

),

products AS (

    SELECT
        product_sk,
        product_id,
        product_sku,
        name AS product_name
    FROM {{ ref('dim_products') }}
    WHERE is_current = true

),

orders AS (

    SELECT
        order_id,
        order_date,
        status,
        branch_country,
        branch_city,
        customer_sk,
        branch_sk,
        date_sk
    FROM {{ ref('fact_orders') }}

)

SELECT

    oi.order_item_id,

    -- Foreign keys
    oi.order_id,
    o.customer_sk,
    o.branch_sk,
    o.date_sk,
    p.product_sk,

    -- Denormalized for LLM queries
    p.product_sku,
    p.product_name,
    o.branch_country,
    o.branch_city,
    o.status        AS order_status,
    o.order_date,

    -- Measures
    oi.quantity,
    oi.price         AS unit_price,
    oi.line_total,

    oi.dbt_loaded_at,
    oi.row_hash,
    oi.dbt_run_id

FROM order_items oi

LEFT JOIN products p
    ON oi.product_id = p.product_id

LEFT JOIN orders o
    ON oi.order_id = o.order_id
