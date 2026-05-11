SELECT
    d.month_name,
    SUM(f.total_amount) AS revenue
FROM {{ ref('fact_orders') }} f
JOIN {{ ref('dim_date') }} d
    ON f.date_sk = d.date_sk
GROUP BY 1