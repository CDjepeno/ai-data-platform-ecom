SELECT

    d.year,

    c.customer_id,
    c.first_name,
    c.last_name,

    SUM(f.total_amount) AS total_revenue

FROM {{ ref('fact_orders') }} f

JOIN {{ ref('dim_customers') }} c
    ON f.customer_sk = c.customer_sk

JOIN {{ ref('dim_date') }} d
    ON f.date_sk = d.date_sk

GROUP BY
    d.year,
    c.customer_id,
    c.first_name,
    c.last_name

ORDER BY
    d.year,
    total_revenue DESC