{{ config(materialized='table') }}

WITH source_data AS (
    SELECT *
    FROM {{ source('raw', 'branches') }}

),

cleaned AS (
    SELECT
        branch_id,
        name,
        city,
        CASE country
            WHEN 'FR' THEN 'France'
            WHEN 'DE' THEN 'Germany'
            WHEN 'ES' THEN 'Spain'
            WHEN 'US' THEN 'United States'
            WHEN 'JP' THEN 'Japan'
            WHEN 'AE' THEN 'United Arab Emirates'
            ELSE country
        END AS country,
        created_at,
        updated_at,
        CURRENT_TIMESTAMP AS dbt_loaded_at,
        '{{ invocation_id }}' AS dbt_run_id,
        TO_HEX(
            MD5(
                TO_UTF8(
                    CONCAT_WS(
                        '|',
                        COALESCE(name, ''),
                        COALESCE(city, ''),
                        COALESCE(country, '')
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
