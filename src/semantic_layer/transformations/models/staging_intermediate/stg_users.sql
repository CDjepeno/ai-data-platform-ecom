{{ config(
    materialized='table',
) }}

WITH source_data AS (
    SELECT *
    FROM {{ source('raw', 'users') }}

),

cleaned AS (
    SELECT
        user_id,
        COALESCE(TRIM(email), 'Unknown') AS email_user,
        TRIM(role) AS role_user,
        created_at,
        updated_at,
        CURRENT_TIMESTAMP AS dbt_loaded_at,
        '{{ invocation_id }}' AS dbt_run_id,
        TO_HEX(
            MD5(
                TO_UTF8(
                    CONCAT_WS(
                        '|',
                        COALESCE(TRIM(email), ''),
                        COALESCE(TRIM(role), '')
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
            PARTITION BY user_id
            ORDER BY updated_at DESC
        ) AS rn
    FROM cleaned
)


SELECT
    user_id,
    email_user AS email,
    role_user AS role,  -- noqa: RF04
    created_at,
    updated_at,
    dbt_loaded_at,
    dbt_run_id,
    row_hash
FROM deduplicated
WHERE rn = 1
