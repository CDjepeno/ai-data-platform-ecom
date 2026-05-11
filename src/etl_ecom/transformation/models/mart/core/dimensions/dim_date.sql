{{ config(materialized='table') }}

WITH dates AS (

    SELECT
        date_day
    FROM UNNEST(
        sequence(
            DATE '2015-01-01',
            DATE '2035-12-31',
            INTERVAL '1' DAY
        )
    ) AS t(date_day)

)

SELECT

    CAST(date_format(date_day, '%Y%m%d') AS INTEGER) AS date_sk,

    date_day AS full_date,

    day_of_week(date_day) AS day_of_week,

    format_datetime(CAST(date_day AS timestamp), 'EEEE') AS day_name,

    day(date_day) AS day_of_month,

    month(date_day) AS month_number,

    format_datetime(CAST(date_day AS timestamp), 'MMMM') AS month_name,

    year(date_day) AS year,

    quarter(date_day) AS quarter,

    concat(
        CAST(year(date_day) AS VARCHAR),
        '-Q',
        CAST(quarter(date_day) AS VARCHAR)
    ) AS year_quarter,

    year(date_day) AS fiscal_year,

    quarter(date_day) AS fiscal_quarter,

    CASE
        WHEN day_of_week(date_day) IN (6, 7)
            THEN true
        ELSE false
    END AS is_weekend,

    false AS is_public_holiday,

    CAST(NULL AS VARCHAR) AS holiday_name,

    CASE
        WHEN year(date_day) = year(current_date)
            THEN true
        ELSE false
    END AS current_year_flag

FROM dates