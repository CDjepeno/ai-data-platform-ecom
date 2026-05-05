-- =========================================
-- 📅 DAILY GROWTH SEED (incremental friendly)
-- =========================================

-- 🔧 FIX SEQUENCES (IMPORTANT 🔥)
SELECT setval('users_user_id_seq', COALESCE((SELECT MAX(user_id) FROM users), 1));
SELECT setval('customers_customer_id_seq', COALESCE((SELECT MAX(customer_id) FROM customers), 1));
SELECT setval('products_product_id_seq', COALESCE((SELECT MAX(product_id) FROM products), 1));
SELECT setval('orders_order_id_seq', COALESCE((SELECT MAX(order_id) FROM orders), 1));


-- 🔥 USERS (50 nouveaux / jour)
INSERT INTO users (email, password_hash, role, created_at, updated_at)
SELECT
    CASE
        WHEN random() < 0.1 THEN NULL
        WHEN random() < 0.05 THEN 'bad_email'
        ELSE 'daily_user_' || floor(random()*1000000) || '@mail.com'
    END,
    'hash',
    CASE
        WHEN random() < 0.05 THEN 'admin'::user_role
        ELSE 'customer'::user_role
    END,
    NOW() + (gs * INTERVAL '1 second'),
    NOW() + (gs * INTERVAL '1 second')
FROM generate_series(1, 50) gs;


-- 🔥 CUSTOMERS (liés aux nouveaux users)
INSERT INTO customers (user_id, first_name, last_name, city, created_at, updated_at)
SELECT
    u.user_id,
    CASE WHEN random() < 0.2 THEN NULL ELSE 'John' END,
    CASE WHEN random() < 0.2 THEN NULL ELSE 'Doe' END,
    (ARRAY['Paris', 'Berlin', 'Madrid'])[floor(random() * 3 + 1)],
    NOW() + (ROW_NUMBER() OVER () * INTERVAL '1 second'),
    NOW() + (ROW_NUMBER() OVER () * INTERVAL '1 second')
FROM (
    SELECT user_id
    FROM users
    ORDER BY user_id DESC
    LIMIT 50
) u;


-- 🔥 PRODUCTS (10 nouveaux / jour)
INSERT INTO products (name, price, created_at, updated_at)
SELECT
    CASE WHEN random() < 0.1 THEN NULL ELSE 'Daily Product ' || floor(random()*100000) END,
    CASE WHEN random() < 0.1 THEN -20 ELSE round((random() * 200)::numeric, 2) END,
    NOW() + (gs * INTERVAL '2 second'),
    NOW() + (gs * INTERVAL '2 second')
FROM generate_series(1, 10) gs;


-- 🔥 ORDERS (100 / jour)
INSERT INTO orders (customer_id, branch_id, status, created_at, updated_at)
SELECT
    (SELECT customer_id FROM customers ORDER BY random() LIMIT 1),
    (SELECT branch_id FROM branches ORDER BY random() LIMIT 1),
    (ARRAY['pending', 'paid', 'cancelled'])[floor(random() * 3 + 1)]::order_status,
    NOW() + (gs * INTERVAL '1 second'),
    NOW() + (gs * INTERVAL '1 second')
FROM generate_series(1, 100) gs;


-- 🔥 ORDER ITEMS (~300 / jour)
INSERT INTO order_items (order_id, product_id, quantity, price)
SELECT
    o.order_id,
    (SELECT product_id FROM products ORDER BY random() LIMIT 1),
    (random() * 5)::int,
    round((random() * 200)::numeric, 2)
FROM (
    SELECT order_id
    FROM orders
    ORDER BY order_id DESC
    LIMIT 100
) o
CROSS JOIN generate_series(1, 3);


-- 🔥 PAYMENTS (~100 / jour)
INSERT INTO payments (order_id, amount, status)
SELECT
    order_id,
    CASE WHEN random() < 0.2 THEN NULL ELSE round((random() * 300)::numeric, 2) END,
    (ARRAY['pending', 'completed', 'failed'])[floor(random() * 3 + 1)]::payment_status
FROM (
    SELECT order_id
    FROM orders
    ORDER BY order_id DESC
    LIMIT 100
) o;


-- 🔥 SHIPMENTS (~100 / jour)
INSERT INTO shipments (order_id, status)
SELECT
    order_id,
    (ARRAY['preparing', 'shipped', 'delivered'])[floor(random() * 3 + 1)]::shipment_status
FROM (
    SELECT order_id
    FROM orders
    ORDER BY order_id DESC
    LIMIT 100
) o;