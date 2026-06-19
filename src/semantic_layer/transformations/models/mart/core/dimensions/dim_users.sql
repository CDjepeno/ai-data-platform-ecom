{{ config(materialized='table') }}

WITH snapshot_users AS (

    SELECT *
    FROM {{ ref('snapshot_users') }}

)

SELECT

    user_id,

    email,
    role,
    created_at,
    updated_at,
    row_hash,
    dbt_valid_from AS valid_from,

    dbt_valid_to AS valid_to,
    dbt_loaded_at,

    ROW_NUMBER() OVER (ORDER BY user_id, dbt_valid_from) AS user_sk,

    COALESCE(dbt_valid_to IS NULL, FALSE) AS is_current

FROM snapshot_users
