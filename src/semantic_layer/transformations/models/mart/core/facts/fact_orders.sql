-- noqa: disable=TMP
{{ config(materialized='table') }}

WITH dim_branches AS (

    SELECT *
    FROM {{ ref('dim_branches') }}
    WHERE is_current = TRUE

),

dim_customers AS (

    SELECT *
    FROM {{ ref('dim_customers') }}
    WHERE is_current = TRUE

),

dim_date AS (

    SELECT *
    FROM {{ ref('dim_date') }}

)

SELECT

    o.order_id,

    -- Foreign Keys vers dimensions
    b.country AS branch_country,
    b.city AS branch_city,
    o.total_amount,

    -- Degenerate dimensions
    o.status,
    o.order_date,

    -- Business measures
    o.created_at,
    COALESCE(b.branch_sk, -1) AS branch_sk,
    COALESCE(c.customer_sk, -1) AS customer_sk,

    COALESCE(d.date_sk, -1) AS date_sk

FROM {{ ref('stg_orders') }} AS o

LEFT JOIN dim_branches AS b
    ON o.branch_id = b.branch_id

LEFT JOIN dim_customers AS c
    ON o.customer_id = c.customer_id

LEFT JOIN dim_date AS d
    ON CAST(o.created_at AS DATE) = d.full_date
