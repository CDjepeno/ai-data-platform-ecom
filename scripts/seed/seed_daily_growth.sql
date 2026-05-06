-- =========================================
-- 📅 DAILY INCREMENTAL SIMULATION (REALISTIC)
-- =========================================

-- 🔥 PARAM : jour simulé
WITH sim AS (
    SELECT CURRENT_DATE AS run_date
)

-- =========================================
-- 🔧 FIX SEQUENCES
-- =========================================
SELECT SETVAL('users_user_id_seq', COALESCE((SELECT MAX(user_id) FROM users), 1));
SELECT SETVAL('customers_customer_id_seq', COALESCE((SELECT MAX(customer_id) FROM customers), 1));
SELECT SETVAL('products_product_id_seq', COALESCE((SELECT MAX(product_id) FROM products), 1));
SELECT SETVAL('orders_order_id_seq', COALESCE((SELECT MAX(order_id) FROM orders), 1));

-- =========================================
-- 👤 USERS (nouveaux + duplications)
-- =========================================
INSERT INTO users (email, password_hash, role, created_at, updated_at)
SELECT
    CASE
        WHEN RANDOM() < 0.1 THEN NULL
        WHEN RANDOM() < 0.05 THEN 'duplicate@mail.com'
        ELSE 'user_' || FLOOR(RANDOM() * 1000000) || '@mail.com'
    END,
    'hash',
    CASE WHEN RANDOM() < 0.05 THEN 'admin' ELSE 'customer' END::user_role,
    sim.run_date + (gs * interval '1 second'),
    sim.run_date + (gs * interval '1 second')
FROM GENERATE_SERIES(1, 50) AS gs, sim;

-- =========================================
-- 🧍 CUSTOMERS
-- =========================================
INSERT INTO customers (user_id, first_name, last_name, city, country, created_at, updated_at)
SELECT
    u.user_id,
    CASE WHEN RANDOM() < 0.2 THEN NULL ELSE 'John' END,
    CASE WHEN RANDOM() < 0.2 THEN NULL ELSE 'Doe' END,
    (ARRAY['Paris', 'Berlin', 'Madrid', 'NY', 'Tokyo', 'Dubai'])[FLOOR(RANDOM() * 6 + 1)],
    (ARRAY['FR', 'DE', 'ES', 'US', 'JP', 'AE'])[FLOOR(RANDOM() * 6 + 1)],
    NOW(),
    NOW()
FROM (
    SELECT user_id FROM users
    ORDER BY user_id DESC LIMIT 50
) AS u;

-- =========================================
-- 🛍️ PRODUCTS (nouveaux + update prix)
-- =========================================
INSERT INTO products (name, price, created_at, updated_at)
SELECT
    'Daily Product ' || FLOOR(RANDOM() * 100000),
    CASE WHEN RANDOM() < 0.1 THEN -20 ELSE ROUND((RANDOM() * 200)::numeric, 2) END,
    NOW(),
    NOW()
FROM GENERATE_SERIES(1, 10);

-- 🔄 CDC PRICE CHANGE
UPDATE products
SET price = price * (1 + (RANDOM() - 0.5))
WHERE RANDOM() < 0.05;

-- =========================================
-- 🧠 ORDERS (réalistes + clients actifs)
-- =========================================
WITH active_customers AS (
    SELECT customer_id FROM customers
    ORDER BY RANDOM() LIMIT 200
)

INSERT INTO orders (customer_id, branch_id, status, order_date, total_amount, created_at, updated_at)
SELECT
    CASE
        WHEN RANDOM() < 0.05 THEN NULL
        WHEN RANDOM() < 0.7
            THEN (
                SELECT customer_id FROM active_customers
                ORDER BY RANDOM() LIMIT 1
            )
        ELSE (
            SELECT customer_id FROM customers
            ORDER BY RANDOM() LIMIT 1
        )
    END,
    (
        SELECT branch_id FROM branches
        ORDER BY RANDOM() LIMIT 1
    ),
    'pending'::order_status,
    NOW(),
    ROUND((RANDOM() * 200 + 20)::numeric, 2),
    NOW(),
    NOW()
FROM GENERATE_SERIES(1, 120);

-- =========================================
-- 🧾 ORDER ITEMS (liés au stock)
-- =========================================
INSERT INTO order_items (order_id, product_id, quantity, price)
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
    ORDER BY order_id DESC LIMIT 120
) AS o
INNER JOIN branch_products AS bp ON o.branch_id = bp.branch_id
ORDER BY RANDOM()
LIMIT 400;

-- =========================================
-- 💳 PAYMENTS (avec incohérences)
-- =========================================
INSERT INTO payments (order_id, amount, status, payment_date)
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
    ORDER BY order_id DESC LIMIT 120
) AS o;

-- =========================================
-- 📦 SHIPMENTS (délai réaliste)
-- =========================================
INSERT INTO shipments (order_id, shipped_date, delivery_date, status)
SELECT
    order_id,
    NOW() + (RANDOM() * interval '2 days'),
    NOW() + (RANDOM() * interval '7 days'),
    (ARRAY['preparing', 'shipped', 'delivered'])[FLOOR(RANDOM() * 3 + 1)]::shipment_status
FROM (
    SELECT order_id FROM orders
    ORDER BY order_id DESC LIMIT 120
) AS o;

-- =========================================
-- 🔁 LATE ARRIVING DATA (🔥 IMPORTANT)
-- =========================================
UPDATE orders
SET updated_at = NOW()
WHERE order_id IN (
    SELECT order_id FROM orders
    ORDER BY RANDOM()
    LIMIT 30
);

-- =========================================
-- 🔄 CDC STATUS CHANGE
-- =========================================
UPDATE orders
SET status = 'paid'
WHERE
    status = 'pending'
    AND RANDOM() < 0.5;

UPDATE orders
SET status = 'cancelled'
WHERE RANDOM() < 0.1;

-- =========================================
-- 💥 ANOMALIES MÉTIER
-- =========================================

-- paiement OK mais commande annulée
UPDATE payments
SET status = 'completed'
WHERE
    RANDOM() < 0.05
    AND order_id IN (
        SELECT order_id FROM orders
        WHERE status = 'cancelled'
    );

-- livraison sans paiement
UPDATE shipments
SET status = 'delivered'
WHERE
    RANDOM() < 0.05
    AND order_id IN (
        SELECT order_id FROM payments
        WHERE status != 'completed'
    );

-- stock décrémenté (simulation vente)
UPDATE branch_products
SET stock = stock - (RANDOM() * 3)::int
WHERE RANDOM() < 0.2;

-- rupture stock
UPDATE branch_products
SET stock = -5
WHERE RANDOM() < 0.02;
