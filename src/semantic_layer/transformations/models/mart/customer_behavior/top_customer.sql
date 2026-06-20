SELECT

    d.year,

    c.customer_id,
    c.first_name,
    c.last_name,

    SUM(f.total_amount) AS total_revenue

FROM {{ ref('fact_orders') }} AS f

INNER JOIN {{ ref('dim_customers') }} AS c
    ON f.customer_sk = c.customer_sk

INNER JOIN {{ ref('dim_date') }} AS d
    ON f.date_sk = d.date_sk

GROUP BY
    d.year,
    c.customer_id,
    c.first_name,
    c.last_name

ORDER BY
    d.year ASC,
    total_revenue DESC
