SELECT
    f.customer_sk,
    c.first_name,
    c.last_name,

    SUM(f.total_amount) AS total_revenue,
    COUNT(f.order_id) AS total_orders,
    AVG(f.total_amount) AS avg_order_value
FROM {{ ref('fact_orders') }} AS f
INNER JOIN {{ ref('dim_customers') }} AS c
    ON f.customer_sk = c.customer_sk
GROUP BY 1, 2, 3
