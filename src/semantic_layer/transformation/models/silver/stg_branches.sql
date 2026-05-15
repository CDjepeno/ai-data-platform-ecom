{{ config(materialized='table') }}

WITH source_data AS (
    SELECT  *
    FROM {{ source('raw', 'branches') }}

),

cleaned AS (
    SELECT  
    branch_id,
    name,
    city,
    country,
    created_at,
    updated_at,
    ingested_at,
    CURRENT_TIMESTAMP AS dbt_loaded_at,
    '{{ invocation_id }}' AS dbt_run_id,
    to_hex(
        md5(
            to_utf8(
                concat_ws(
                    '|',
                    coalesce(name, ''),
                    coalesce(city, ''),
                    coalesce(country, '')
                )
            )
        )
    ) AS row_hash
FROM source_data
),

deduplicated AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (
            PARTITION BY branch_id 
            ORDER BY updated_at DESC
        ) AS rn
    FROM cleaned
)


SELECT 
    branch_id,
    name,
    city,
    country,
    created_at,
    updated_at,
    dbt_loaded_at,
    row_hash,
    dbt_run_id
FROM deduplicated
WHERE rn = 1