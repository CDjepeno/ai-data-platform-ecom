{{ config(materialized='table') }}

WITH snapshot_branches AS (

    SELECT *
    FROM {{ ref('snapshot_branches') }}

)

SELECT

    ROW_NUMBER() OVER (
        ORDER BY dbt_valid_from, branch_id
    ) AS branch_sk,

    branch_id,
    name,
    city,
    country,


    dbt_valid_from AS valid_from,
    dbt_valid_to AS valid_to,

     CASE
        WHEN dbt_valid_to IS NULL
            THEN true
        ELSE false
    END AS is_current,

    dbt_loaded_at,
    row_hash
    

FROM snapshot_branches