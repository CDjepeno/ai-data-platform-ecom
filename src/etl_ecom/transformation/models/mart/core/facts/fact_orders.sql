{{ config(materialized='table') }}

WITH orders AS (

    SELECT *
    FROM {{ ref('stg_orders') }}

),

dim_branches AS (

    SELECT *
    FROM {{ ref('dim_branches') }}
    WHERE is_current = true

),

dim_customers AS (

    SELECT *
    FROM {{ ref('dim_customers') }}
    WHERE is_current = true

),

dim_date AS (

    SELECT *
    FROM {{ ref('dim_date') }}

)

SELECT

    o.order_id,

    -- Foreign Keys vers dimensions
    COALESCE(b.branch_sk, -1) AS branch_sk,
    COALESCE(c.customer_sk, -1) AS customer_sk,
    COALESCE(d.date_sk, -1) AS date_sk,

    -- Business measures
    o.total_amount,
    o.status,
    o.order_date,

    o.created_at

FROM {{ ref('stg_orders') }} o

LEFT JOIN {{ ref('dim_branches') }} b
    ON o.branch_id = b.branch_id
    AND b.is_current = true

LEFT JOIN {{ ref('dim_customers') }} c
    ON o.customer_id = c.customer_id
    AND c.is_current = true

LEFT JOIN {{ ref('dim_date') }} d
    ON CAST(o.created_at AS DATE) = d.full_date