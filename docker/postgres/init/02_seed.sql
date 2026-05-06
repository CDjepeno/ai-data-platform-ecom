-- ============================================
-- 🌍 MARKETPLACE MULTI-BRANCH SEED (REALISTIC)
-- ============================================

-- =============================
-- BRANCHES (GLOBAL)
-- =============================
INSERT INTO branches (name, city, country)
VALUES
('Paris Store', 'Paris', 'FR'),
('Berlin Store', 'Berlin', 'DE'),
('Madrid Store', 'Madrid', 'ES'),
('New York Store', 'New York', 'US'),
('Tokyo Store', 'Tokyo', 'JP'),
('Dubai Store', 'Dubai', 'AE');

-- =============================
-- USERS
-- =============================
INSERT INTO users (email, password_hash, role, created_at, updated_at)
SELECT
    CASE
        WHEN random() < 0.1 THEN NULL
        WHEN random() < 0.05 THEN 'duplicate@mail.com'
        ELSE 'user' || gs || '@mail.com'
    END,
    'hash',
    CASE WHEN random() < 0.05 THEN 'admin' ELSE 'customer' END::user_role,
    now() - (random() * interval '180 days'),
    now() - (random() * interval '10 days')
FROM generate_series(1, 2000) AS gs;

-- =============================
-- CUSTOMERS
-- =============================
INSERT INTO customers (user_id, first_name, last_name, city, country)
SELECT
    user_id,
    CASE WHEN random() < 0.2 THEN NULL ELSE 'John' END,
    CASE WHEN random() < 0.2 THEN NULL ELSE 'Doe' END,
    (ARRAY['Paris', 'Berlin', 'Madrid', 'NY', 'Tokyo', 'Dubai'])[floor(random() * 6 + 1)],
    (ARRAY['FR', 'DE', 'ES', 'US', 'JP', 'AE'])[floor(random() * 6 + 1)]
FROM users;

-- =============================
-- PRODUCTS
-- =============================
INSERT INTO products (name, price, created_at)
SELECT
    'Product ' || gs,
    CASE
        WHEN random() < 0.05 THEN -10
        WHEN random() < 0.02 THEN 99999
        ELSE round((random() * 300)::numeric, 2)
    END,
    now() - (random() * interval '365 days')
FROM generate_series(1, 800) AS gs;

-- =============================
-- STOCK PAR BRANCH (🔥 IMPORTANT)
-- =============================
INSERT INTO branch_products (branch_id, product_id, stock)
SELECT
    b.branch_id,
    p.product_id,
    CASE
        WHEN random() < 0.1 THEN 0
        WHEN random() < 0.05 THEN -10 -- anomalie
        ELSE (random() * 100)::int
    END
FROM branches AS b
CROSS JOIN products AS p
WHERE random() < 0.3; -- tous les produits ne sont pas partout

-- =============================
-- ORDERS (LOGIQUE RÉALISTE)
-- =============================
WITH active_customers AS (
    SELECT customer_id FROM customers
    ORDER BY random()
    LIMIT 400
)

INSERT INTO orders (customer_id, branch_id, status, order_date, total_amount)
SELECT
    CASE
        WHEN random() < 0.05 THEN NULL
        WHEN random() < 0.7
            THEN (
                SELECT customer_id FROM active_customers
                ORDER BY random() LIMIT 1
            )
        ELSE (
            SELECT customer_id FROM customers
            ORDER BY random() LIMIT 1
        )
    END,
    (
        SELECT branch_id FROM branches
        ORDER BY random() LIMIT 1
    ),
    (ARRAY['pending', 'paid', 'cancelled'])[floor(random() * 3 + 1)]::order_status,
    now() - (random() * interval '60 days'),
    round((random() * 200 + 20)::numeric, 2)
FROM generate_series(1, 5000);

-- =============================
-- ORDER ITEMS (LIÉS AU STOCK)
-- =============================
INSERT INTO order_items (order_id, product_id, quantity, price)
SELECT
    o.order_id,
    bp.product_id,
    greatest(1, (random() * 5)::int),
    round((random() * 100)::numeric, 2)
FROM orders AS o
INNER JOIN branch_products AS bp ON o.branch_id = bp.branch_id
ORDER BY random()
LIMIT 15000;

-- =============================
-- PAYMENTS
-- =============================
INSERT INTO payments (order_id, amount, status)
SELECT
    order_id,
    CASE
        WHEN random() < 0.1 THEN NULL
        WHEN random() < 0.05 THEN -50
        ELSE total_amount
    END,
    CASE
        WHEN random() < 0.7 THEN 'completed'
        WHEN random() < 0.2 THEN 'failed'
        ELSE 'pending'
    END::payment_status
FROM orders;

-- =============================
-- SHIPMENTS
-- =============================
INSERT INTO shipments (order_id, shipped_date, delivery_date, status)
SELECT
    order_id,
    order_date + (random() * interval '3 days'),
    order_date + (random() * interval '10 days'),
    (ARRAY['preparing', 'shipped', 'delivered'])[floor(random() * 3 + 1)]::shipment_status
FROM orders;

-- ============================================
-- 💥 ANOMALIES MÉTIER (IMPORTANT)
-- ============================================

-- Paiement validé sur commande annulée
UPDATE payments
SET status = 'completed'
WHERE
    random() < 0.05
    AND order_id IN (
        SELECT order_id FROM orders
        WHERE status = 'cancelled'
    );

-- Livraison sans paiement
UPDATE shipments
SET status = 'delivered'
WHERE
    random() < 0.05
    AND order_id IN (
        SELECT order_id FROM payments
        WHERE status != 'completed'
    );

-- Stock négatif (déjà injecté + aggravation)
UPDATE branch_products
SET stock = stock - 50
WHERE random() < 0.05;

-- total incohérent
UPDATE orders
SET total_amount = total_amount * (random() * 3)
WHERE random() < 0.1;

-- doublons email
INSERT INTO users (email, password_hash, role)
SELECT
    email,
    'hash',
    role
FROM users
WHERE random() < 0.05;
