{{ config(materialized='table') }}

WITH unknown_record AS (

    SELECT

        -1 AS customer_sk,
        -1 AS customer_id,
        'Unknown' AS first_name,
        'Unknown' AS last_name,
        'Unknown' AS email,
        'Unknown' AS address,
        'Unknown' AS city,
        'Unknown' AS country,
        CAST(NULL AS TIMESTAMP) AS created_at,
        CAST(NULL AS TIMESTAMP) AS updated_at,
        NULL AS row_hash,
        CAST(NULL AS TIMESTAMP) AS valid_from,
        CAST(NULL AS TIMESTAMP) AS valid_to,

        true AS is_current,
        CAST(NULL AS TIMESTAMP) AS dbt_loaded_at

),

snapshot_customers AS (

    SELECT *
    FROM {{ ref('snapshot_customers') }}

),

real_customers AS (

    SELECT

        ROW_NUMBER() OVER (
            ORDER BY dbt_valid_from, customer_id
        ) AS customer_sk,

        customer_id,
        first_name,
        last_name,
        phone,
        address,
        city,
        country,
        created_at,
        updated_at,
        row_hash,


        dbt_valid_from AS valid_from,
        dbt_valid_to AS valid_to,

        CASE
            WHEN dbt_valid_to IS NULL
                THEN true
            ELSE false
        END AS is_current,

        dbt_loaded_at

    FROM snapshot_customers
)


SELECT *
FROM unknown_record

UNION ALL

SELECT *
FROM real_customers