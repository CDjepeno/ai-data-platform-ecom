-- noqa: disable=TMP
{{ config(materialized='table') }}

WITH snapshot_branches AS (

    SELECT *
    FROM {{ ref('snapshot_branches') }}

)

SELECT

    branch_id,

    name,
    city,
    country,
    dbt_valid_from AS valid_from,

    dbt_valid_to AS valid_to,
    dbt_loaded_at,

    row_hash,

    ROW_NUMBER() OVER (
        ORDER BY dbt_valid_from, branch_id
    ) AS branch_sk,
    COALESCE(dbt_valid_to IS NULL, FALSE) AS is_current

FROM snapshot_branches
