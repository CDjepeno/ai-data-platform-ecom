SELECT
    f.customer_sk,
    c.first_name,
    c.last_name,

    SUM(f.total_amount) AS total_revenue,
    COUNT(f.order_id) AS total_orders,
    AVG(f.total_amount) AS avg_order_value
FROM {{ ref('fact_orders') }} f
JOIN {{ ref('dim_customers') }} c
    ON f.customer_sk = c.customer_sk
GROUP BY 1,2,3