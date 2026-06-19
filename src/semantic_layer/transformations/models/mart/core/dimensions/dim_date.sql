{{ config(materialized='table') }}

WITH dates AS (

    SELECT date_day
    FROM UNNEST(
        SEQUENCE(
            DATE '2015-01-01',
            DATE '2035-12-31',
            INTERVAL '1' DAY
        )
    ) AS t (date_day)

)

SELECT

    CAST(DATE_FORMAT(date_day, '%Y%m%d') AS INTEGER) AS date_sk,

    date_day AS full_date,

    FALSE AS is_public_holiday,

    CAST(NULL AS VARCHAR) AS holiday_name,

    DAY_OF_WEEK(date_day) AS day_of_week,

    FORMAT_DATETIME(CAST(date_day AS TIMESTAMP), 'EEEE') AS day_name,

    DAY(date_day) AS day_of_month,

    MONTH(date_day) AS month_number,

    FORMAT_DATETIME(CAST(date_day AS TIMESTAMP), 'MMMM') AS month_name,

    YEAR(date_day) AS year,  -- noqa: RF04

    QUARTER(date_day) AS quarter,  -- noqa: RF04

    CONCAT(
        CAST(YEAR(date_day) AS VARCHAR),
        '-Q',
        CAST(QUARTER(date_day) AS VARCHAR)
    ) AS year_quarter,

    YEAR(date_day) AS fiscal_year,

    QUARTER(date_day) AS fiscal_quarter,

    COALESCE(DAY_OF_WEEK(date_day) IN (6, 7), FALSE) AS is_weekend,

    COALESCE(YEAR(date_day) = YEAR(CURRENT_DATE), FALSE) AS current_year_flag

FROM dates
