{{ config(materialized='table') }}

select
    current_date as date_day