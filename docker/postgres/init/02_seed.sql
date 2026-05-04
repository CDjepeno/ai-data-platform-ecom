-- USERS (~1000)
INSERT INTO users (email, password_hash, role)
SELECT 
    CASE 
        WHEN random() < 0.2 THEN NULL
        WHEN random() < 0.1 THEN 'bad_email'
        ELSE 'user' || gs || '@mail.com'
    END,
    'hash',
    CASE 
        WHEN random() < 0.1 THEN 'admin'::user_role
        ELSE 'customer'::user_role
    END
FROM generate_series(1,1000) gs;

-- CUSTOMERS (~900)
INSERT INTO customers (user_id, first_name, last_name, city)
SELECT 
    user_id,
    CASE WHEN random() < 0.2 THEN NULL ELSE 'John' END,
    CASE WHEN random() < 0.2 THEN NULL ELSE 'Doe' END,
    (ARRAY['Paris','Berlin','Madrid'])[floor(random()*3+1)]
FROM users;

-- PRODUCTS (~500)
INSERT INTO products (name, price)
SELECT 
    CASE WHEN random() < 0.1 THEN NULL ELSE 'Product ' || gs END,
    CASE WHEN random() < 0.1 THEN -50 ELSE round((random()*200)::numeric, 2) END
FROM generate_series(1,500) gs;

-- BRANCHES
INSERT INTO branches (name) VALUES ('Paris'), ('Berlin'), ('Madrid');

-- ORDERS (~3000)
INSERT INTO orders (customer_id, branch_id, status)
SELECT 
    (SELECT customer_id FROM customers ORDER BY random() LIMIT 1),
    (SELECT branch_id FROM branches ORDER BY random() LIMIT 1),
    (ARRAY['pending','paid','cancelled'])[floor(random()*3+1)]::order_status
FROM generate_series(1,3000);

-- ORDER ITEMS (~8000)
INSERT INTO order_items (order_id, product_id, quantity, price)
SELECT 
    o.order_id,
    (SELECT product_id FROM products ORDER BY random() LIMIT 1),
    (random()*5)::int,
    round((random()*200)::numeric, 2)
FROM orders o
CROSS JOIN generate_series(1,3);

-- PAYMENTS
INSERT INTO payments (order_id, amount, status)
SELECT 
    order_id,
    CASE WHEN random() < 0.2 THEN NULL ELSE round((random()*300)::numeric,2)  END,
    (ARRAY['pending','completed','failed'])[floor(random()*3+1)]::payment_status
FROM orders;

-- SHIPMENTS
INSERT INTO shipments (order_id, status)
SELECT 
    order_id,
    (ARRAY['preparing','shipped','delivered'])[floor(random()*3+1)]::shipment_status
FROM orders;