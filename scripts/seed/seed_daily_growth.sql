-- =========================================
-- 📅 DAILY INCREMENTAL SIMULATION (REALISTIC)
-- PostgreSQL
-- =========================================

-- =========================================
-- 🔥 PARAM: simulated day
-- =========================================
WITH sim AS (
    SELECT CURRENT_DATE AS run_date
)

SELECT run_date FROM sim;

-- =========================================
-- 🔧 FIX SEQUENCES
-- =========================================

SELECT SETVAL(
    'users_user_id_seq',
    COALESCE((SELECT MAX(user_id) FROM users), 1)
);

SELECT SETVAL(
    'customers_customer_id_seq',
    COALESCE((SELECT MAX(customer_id) FROM customers), 1)
);

SELECT SETVAL(
    'products_product_id_seq',
    COALESCE((SELECT MAX(product_id) FROM products), 1)
);

SELECT SETVAL(
    'orders_order_id_seq',
    COALESCE((SELECT MAX(order_id) FROM orders), 1)
);

-- =========================================
-- 👤 USERS (new + duplicates)
-- =========================================

INSERT INTO users (
    email,
    password_hash,
    role,
    created_at,
    updated_at
)
SELECT
    CASE
        WHEN RANDOM() < 0.1 THEN NULL
        WHEN RANDOM() < 0.05 THEN 'duplicate@mail.com'
        ELSE 'user_' || FLOOR(RANDOM() * 1000000) || '@mail.com'
    END,
    'hash',
    CASE
        WHEN RANDOM() < 0.05
            THEN 'admin'
        ELSE 'customer'
    END::user_role,
    NOW(),
    NOW()
FROM GENERATE_SERIES(1, 50);

-- =========================================
-- 🧍 CUSTOMERS
-- avoid duplicate user_id
-- =========================================

INSERT INTO customers (
    user_id,
    first_name,
    last_name,
    city,
    country,
    created_at,
    updated_at
)
SELECT
    u.user_id,

    CASE
        WHEN RANDOM() < 0.2 THEN NULL
        ELSE (
            ARRAY[
                'John',
                'Emma',
                'Lucas',
                'Sophia',
                'Noah',
                'Liam',
                'Olivia',
                'Mia'
            ]
        )[FLOOR(RANDOM() * 8 + 1)]
    END,

    CASE
        WHEN RANDOM() < 0.2 THEN NULL
        ELSE (
            ARRAY[
                'Smith',
                'Doe',
                'Martin',
                'Garcia',
                'Lee',
                'Brown',
                'Wilson',
                'Taylor'
            ]
        )[FLOOR(RANDOM() * 8 + 1)]
    END,

    (
        ARRAY[
            'Paris',
            'Berlin',
            'Madrid',
            'New York',
            'Tokyo',
            'Dubai'
        ]
    )[FLOOR(RANDOM() * 6 + 1)],

    (
        ARRAY[
            'FR',
            'DE',
            'ES',
            'US',
            'JP',
            'AE'
        ]
    )[FLOOR(RANDOM() * 6 + 1)],

    NOW(),
    NOW()

FROM users u

LEFT JOIN customers c
    ON u.user_id = c.user_id

WHERE c.user_id IS NULL

ORDER BY u.user_id DESC
LIMIT 50;

-- =========================================
-- 🛍️ PRODUCTS (new)
-- =========================================

INSERT INTO products (
    name,
    price,
    created_at,
    updated_at
)
SELECT
    'Daily Product ' || FLOOR(RANDOM() * 100000),

    CASE
        WHEN RANDOM() < 0.05 THEN -20
        WHEN RANDOM() < 0.02 THEN 99999
        ELSE ROUND((RANDOM() * 200)::numeric, 2)
    END,

    NOW(),
    NOW()

FROM GENERATE_SERIES(1, 10);

-- =========================================
-- 🏷️ PRODUCT CATEGORIES
-- =========================================

INSERT INTO product_categories (
    product_id,
    category_id
)
SELECT
    p.product_id,

    (
        SELECT category_id
        FROM categories
        ORDER BY RANDOM()
        LIMIT 1
    )

FROM (
    SELECT product_id
    FROM products
    ORDER BY product_id DESC
    LIMIT 10
) p;

-- =========================================
-- 🔄 CDC PRICE CHANGE
-- avoid runaway prices
-- =========================================

UPDATE products
SET price = GREATEST(
    1,
    LEAST(
        ROUND(
            (
                price * (
                    1 + (RANDOM() * 0.2 - 0.1)
                )
            )::numeric,
            2
        ),
        5000
    )
)
WHERE RANDOM() < 0.05;

-- =========================================
-- 🧠 ORDERS
-- active customers + realistic activity
-- =========================================

WITH active_customers AS (
    SELECT customer_id
    FROM customers
    ORDER BY RANDOM()
    LIMIT 200
)

INSERT INTO orders (
    customer_id,
    branch_id,
    status,
    order_date,
    total_amount,
    created_at,
    updated_at
)
SELECT
    CASE
        WHEN RANDOM() < 0.05 THEN NULL

        WHEN RANDOM() < 0.7 THEN (
            SELECT customer_id
            FROM active_customers
            ORDER BY RANDOM()
            LIMIT 1
        )

        ELSE (
            SELECT customer_id
            FROM customers
            ORDER BY RANDOM()
            LIMIT 1
        )
    END,

    (
        SELECT branch_id
        FROM branches
        ORDER BY RANDOM()
        LIMIT 1
    ),

    'pending'::order_status,

    NOW(),

    ROUND((RANDOM() * 200 + 20)::numeric, 2),

    NOW(),
    NOW()

FROM GENERATE_SERIES(1, 120);

-- =========================================
-- 🧾 ORDER ITEMS
-- tied to available stock
-- =========================================

INSERT INTO order_items (
    order_id,
    product_id,
    quantity,
    price
)
SELECT
    o.order_id,

    bp.product_id,

    GREATEST(1, (RANDOM() * 5)::int),

    ROUND((RANDOM() * 100)::numeric, 2)

FROM (
    SELECT
        order_id,
        branch_id
    FROM orders
    ORDER BY order_id DESC
    LIMIT 120
) o

INNER JOIN branch_products bp
    ON o.branch_id = bp.branch_id

ORDER BY RANDOM()

LIMIT 400;

-- =========================================
-- 💳 PAYMENTS
-- =========================================

INSERT INTO payments (
    order_id,
    amount,
    status,
    payment_date
)
SELECT
    order_id,

    CASE
        WHEN RANDOM() < 0.1 THEN NULL
        WHEN RANDOM() < 0.05 THEN -50
        ELSE total_amount
    END,

    CASE
        WHEN RANDOM() < 0.6 THEN 'completed'
        WHEN RANDOM() < 0.2 THEN 'failed'
        ELSE 'pending'
    END::payment_status,

    NOW()

FROM (
    SELECT
        order_id,
        total_amount
    FROM orders
    ORDER BY order_id DESC
    LIMIT 120
) o;

-- =========================================
-- 📦 SHIPMENTS
-- =========================================

INSERT INTO shipments (
    order_id,
    shipped_date,
    delivery_date,
    status
)
SELECT
    order_id,

    NOW() + (RANDOM() * interval '2 days'),

    NOW() + (RANDOM() * interval '7 days'),

    (
        ARRAY[
            'preparing',
            'shipped',
            'delivered'
        ]
    )[FLOOR(RANDOM() * 3 + 1)]::shipment_status

FROM (
    SELECT order_id
    FROM orders
    ORDER BY order_id DESC
    LIMIT 120
) o;

-- =========================================
-- 🔁 LATE ARRIVING DATA
-- =========================================

UPDATE orders
SET updated_at = NOW()
WHERE order_id IN (
    SELECT order_id
    FROM orders
    ORDER BY RANDOM()
    LIMIT 30
);

-- =========================================
-- 🔄 CDC STATUS CHANGE
-- =========================================

UPDATE orders
SET
    status = 'paid',
    updated_at = NOW()
WHERE
    status = 'pending'
    AND RANDOM() < 0.5;

UPDATE orders
SET
    status = 'cancelled',
    updated_at = NOW()
WHERE RANDOM() < 0.1;

-- =========================================
-- 💥 BUSINESS ANOMALIES
-- =========================================

-- payment OK on cancelled order
UPDATE payments
SET status = 'completed'
WHERE
    RANDOM() < 0.05
    AND order_id IN (
        SELECT order_id
        FROM orders
        WHERE status = 'cancelled'
    );

-- shipment without payment
UPDATE shipments
SET status = 'delivered'
WHERE
    RANDOM() < 0.05
    AND order_id IN (
        SELECT order_id
        FROM payments
        WHERE status != 'completed'
    );

-- stock decremented
-- avoid runaway negative values
UPDATE branch_products
SET stock =
    CASE
        WHEN stock > 0
            THEN stock - (RANDOM() * 3)::int
        ELSE stock
    END
WHERE RANDOM() < 0.2;

-- intentional stock-out
UPDATE branch_products
SET stock = -5
WHERE RANDOM() < 0.02;

-- products without category
DELETE FROM product_categories
WHERE RANDOM() < 0.01;

-- inconsistent total
UPDATE orders
SET total_amount = total_amount * (1 + RANDOM())
WHERE RANDOM() < 0.03;

-- delivery before shipment
UPDATE shipments
SET delivery_date = shipped_date - interval '1 day'
WHERE RANDOM() < 0.005;

-- =========================================
-- ✅ QUICK CHECKS
-- =========================================

-- SELECT COUNT(*) FROM users;
-- SELECT COUNT(*) FROM customers;
-- SELECT COUNT(*) FROM products;
-- SELECT COUNT(*) FROM orders;
-- SELECT COUNT(*) FROM payments;
-- SELECT COUNT(*) FROM shipments;