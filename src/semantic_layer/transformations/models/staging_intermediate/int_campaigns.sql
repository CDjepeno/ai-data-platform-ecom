{{ config(materialized='table') }}

SELECT * FROM {{ ref('stg_meta_campaigns') }}
UNION ALL
SELECT * FROM {{ ref('stg_tiktok_campaigns') }}
UNION ALL
SELECT * FROM {{ ref('stg_google_campaigns') }}
