{{ config(materialized='table') }}

WITH snapshot_products AS (

    SELECT *
    FROM {{ ref('snapshot_products') }}

)

SELECT

    product_id,

    product_sku,
    name,
    description,
    price,
    dbt_valid_from AS valid_from,

    dbt_valid_to AS valid_to,
    dbt_loaded_at,

    row_hash,

    ROW_NUMBER() OVER (ORDER BY product_id, dbt_valid_from) AS product_sk,
    COALESCE(dbt_valid_to IS NULL, FALSE) AS is_current

FROM snapshot_products
