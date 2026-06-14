{{ config(materialized='table') }}

WITH snapshot_products AS (

    SELECT *
    FROM {{ ref('snapshot_products') }}

)

SELECT

    ROW_NUMBER() OVER (ORDER BY product_id, dbt_valid_from) AS product_sk,

    product_id,
    product_sku,
    name,
    description,
    price,

    dbt_valid_from  AS valid_from,
    dbt_valid_to    AS valid_to,

    CASE
        WHEN dbt_valid_to IS NULL
            THEN true
        ELSE false
    END AS is_current,

    dbt_loaded_at,
    row_hash

FROM snapshot_products
