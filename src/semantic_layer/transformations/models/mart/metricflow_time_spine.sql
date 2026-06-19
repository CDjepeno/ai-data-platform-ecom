{{ config(materialized='table') }}

SELECT current_date AS date_day
