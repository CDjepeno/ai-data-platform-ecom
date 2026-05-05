-- ==============================
-- SEED DATA - DIRTY VERSION (REALISTIC)
-- ==============================

-- USERS (~1000)
INSERT INTO users (email, password_hash, role, created_at, updated_at)
SELECT
    CASE
        WHEN random() < 0.2 THEN NULL
        WHEN random() < 0.1 THEN 'bad_email'
        WHEN random() < 0.05 THEN '[duplicate@mail.com](mailto:duplicate@mail.com)'
        ELSE 'user' || gs || '@mail.com'
    END,
    'hash',
    CASE
        WHEN random() < 0.1 THEN 'admin'::user_role
        ELSE 'customer'::user_role
    END,
    now() - (random() * interval '60 days'),
    now() - (random() * interval '5 days')
FROM generate_series(1, 1000) AS gs;

-- CUSTOMERS (~1000)
INSERT INTO customers (user_id, first_name, last_name, city, created_at, updated_at)
SELECT
    user_id,
    CASE WHEN random() < 0.3 THEN NULL ELSE 'John' END,
    CASE WHEN random() < 0.3 THEN NULL ELSE 'Doe' END,
    (ARRAY['Paris', 'Berlin', 'Madrid', NULL])[floor(random() * 4 + 1)],
    now() - (random() * interval '60 days'),
    now() - (random() * interval '5 days')
FROM users;

-- PRODUCTS (~500)
INSERT INTO products (name, price, created_at, updated_at)
SELECT
    CASE WHEN random() < 0.15 THEN NULL ELSE 'Product ' || gs END,
    CASE
        WHEN random() < 0.1 THEN -50 -- prix négatif
        WHEN random() < 0.05 THEN 999999 -- outlier
        ELSE round((random() * 200)::numeric, 2)
    END,
    now() - (random() * interval '90 days'),
    now() - (random() * interval '10 days')
FROM generate_series(1, 500) AS gs;

-- BRANCHES
INSERT INTO branches (name, city, country, created_at, updated_at)
VALUES
('Paris Store', 'Paris', 'FR', now(), now()),
('Berlin Store', 'Berlin', 'DE', now(), now()),
('Madrid Store', 'Madrid', 'ES', now(), now());

-- ORDERS (~3000)
INSERT INTO orders (customer_id, branch_id, status, total_amount, created_at, updated_at)
SELECT
    CASE
        WHEN random() < 0.05 THEN NULL -- orphelin
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
    round((random() * 500)::numeric, 2),
    now() - (random() * interval '30 days'),
    now() - (random() * interval '2 days')
FROM generate_series(1, 3000);

-- ORDER ITEMS (~9000)
INSERT INTO order_items (order_id, product_id, quantity, price, created_at, updated_at)
SELECT
    o.order_id,
    (
        SELECT product_id FROM products
        ORDER BY random() LIMIT 1
    ),
    CASE
        WHEN random() < 0.05 THEN -1 -- quantité invalide
        ELSE (random() * 5)::int
    END,
    round((random() * 200)::numeric, 2),
    now() - (random() * interval '30 days'),
    now() - (random() * interval '2 days')
FROM orders AS o
CROSS JOIN generate_series(1, 3);

-- PAYMENTS
INSERT INTO payments (order_id, amount, status, created_at, updated_at)
SELECT
    order_id,
    CASE
        WHEN random() < 0.2 THEN NULL
        WHEN random() < 0.05 THEN -100 -- incohérent
        ELSE round((random() * 300)::numeric, 2)
    END,
    (ARRAY['pending', 'completed', 'failed'])[floor(random() * 3 + 1)]::payment_status,
    now() - (random() * interval '15 days'),
    now() - (random() * interval '1 day')
FROM orders;

-- SHIPMENTS
INSERT INTO shipments (order_id, status, created_at, updated_at)
SELECT
    order_id,
    (ARRAY['preparing', 'shipped', 'delivered'])[floor(random() * 3 + 1)]::shipment_status,
    now() - (random() * interval '15 days'),
    now() - (random() * interval '1 day')
FROM orders;

-- ==============================
-- 🔥 POST-SEED ANOMALIES
-- ==============================

-- incohérences temporelles
UPDATE users
SET updated_at = created_at - interval '2 days'
WHERE random() < 0.1;

-- late arriving data (important pour incremental)
UPDATE orders
SET updated_at = now()
WHERE order_id < 50;

-- incohérence business
UPDATE orders
SET total_amount = total_amount * (random() * 2)
WHERE random() < 0.2;

-- doublons email
INSERT INTO users (email, password_hash, role)
SELECT
    email,
    'hash',
    role
FROM users
WHERE random() < 0.05;
