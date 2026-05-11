{{ config(materialized='table') }}

WITH snapshot_users AS (

    SELECT *
    FROM {{ ref('snapshot_users') }}

)

SELECT

    ROW_NUMBER() OVER () AS user_sk,

    user_id,
    email,
    role,
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

FROM snapshot_users