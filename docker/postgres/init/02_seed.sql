-- ============================================
-- 🌍 MARKETPLACE MULTI-BRANCH SEED (REALISTIC)
-- ============================================

-- ============================================
-- CLEAN
-- ============================================

TRUNCATE TABLE
    shipments,
    payments,
    order_items,
    orders,
    branch_products,
    product_categories,
    products,
    categories,
    customers,
    users,
    branches
RESTART IDENTITY CASCADE;

-- ============================================
-- BRANCHES
-- ============================================

INSERT INTO branches (name, city, country)
VALUES
('Paris Store', 'Paris', 'FR'),
('Berlin Store', 'Berlin', 'DE'),
('Madrid Store', 'Madrid', 'ES'),
('New York Store', 'New York', 'US'),
('Tokyo Store', 'Tokyo', 'JP'),
('Dubai Store', 'Dubai', 'AE');

-- ============================================
-- CATEGORIES
-- ============================================

INSERT INTO categories (name)
VALUES
('Electronics'),
('Clothing'),
('Books'),
('Home'),
('Sports'),
('Beauty'),
('Gaming'),
('Food'),
('Shoes'),
('Accessories'),
('Toys'),
('Office');

-- ============================================
-- USERS
-- ============================================

INSERT INTO users (
    email,
    password_hash,
    role,
    created_at,
    updated_at
)
SELECT
    CASE
        WHEN random() < 0.1 THEN NULL
        WHEN random() < 0.05 THEN 'duplicate@mail.com'
        ELSE 'user' || gs || '@mail.com'
    END,
    'hash',
    CASE
        WHEN random() < 0.05
            THEN 'admin'
        ELSE 'customer'
    END::user_role,
    now() - (random() * interval '180 days'),
    now() - (random() * interval '10 days')
FROM generate_series(1, 2000) AS gs;

-- ============================================
-- CUSTOMERS
-- ============================================

INSERT INTO customers (
    user_id,
    first_name,
    last_name,
    city,
    country
)
SELECT
    user_id,
    CASE
        WHEN random() < 0.2 THEN NULL
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
        )[floor(random() * 8 + 1)]
    END,
    CASE
        WHEN random() < 0.2 THEN NULL
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
        )[floor(random() * 8 + 1)]
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
    )[floor(random() * 6 + 1)],
    (
        ARRAY[
            'FR',
            'DE',
            'ES',
            'US',
            'JP',
            'AE'
        ]
    )[floor(random() * 6 + 1)]
FROM users;

-- ============================================
-- PRODUCTS
-- ============================================

INSERT INTO products (
    name,
    price,
    created_at
)
SELECT
    (
        ARRAY[
            'Laptop',
            'Keyboard',
            'Mouse',
            'Headphones',
            'Monitor',
            'Chair',
            'Desk',
            'Shoes',
            'Backpack',
            'Watch',
            'Phone',
            'Tablet'
        ]
    )[floor(random() * 12 + 1)]
    || ' '
    || gs,
    CASE
        WHEN random() < 0.05 THEN -10
        WHEN random() < 0.02 THEN 99999
        ELSE round((random() * 300)::numeric, 2)
    END,
    now() - (random() * interval '365 days')
FROM generate_series(1, 800) AS gs;

-- ============================================
-- PRODUCT CATEGORIES
-- ============================================

INSERT INTO product_categories (
    product_id,
    category_id
)
SELECT
    p.product_id,
    c.category_id
FROM products p
CROSS JOIN categories c
WHERE random() < 0.15;

-- ============================================
-- STOCK PAR BRANCH
-- ============================================

INSERT INTO branch_products (
    branch_id,
    product_id,
    stock
)
SELECT
    b.branch_id,
    p.product_id,
    CASE
        WHEN random() < 0.1 THEN 0
        WHEN random() < 0.05 THEN -10
        ELSE (random() * 100)::int
    END
FROM branches b
CROSS JOIN products p
WHERE random() < 0.3;

-- ============================================
-- ORDERS
-- ============================================

WITH active_customers AS (
    SELECT customer_id
    FROM customers
    ORDER BY random()
    LIMIT 400
)

INSERT INTO orders (
    customer_id,
    branch_id,
    status,
    order_date,
    total_amount
)
SELECT
    CASE
        WHEN random() < 0.05 THEN NULL
        WHEN random() < 0.7 THEN (
            SELECT customer_id
            FROM active_customers
            ORDER BY random()
            LIMIT 1
        )
        ELSE (
            SELECT customer_id
            FROM customers
            ORDER BY random()
            LIMIT 1
        )
    END,
    (
        SELECT branch_id
        FROM branches
        ORDER BY random()
        LIMIT 1
    ),
    (
        ARRAY[
            'pending',
            'paid',
            'cancelled'
        ]
    )[floor(random() * 3 + 1)]::order_status,
    now() - (random() * interval '60 days'),
    round((random() * 200 + 20)::numeric, 2)
FROM generate_series(1, 5000);

-- ============================================
-- ORDER ITEMS
-- ============================================

INSERT INTO order_items (
    order_id,
    product_id,
    quantity,
    price
)
SELECT
    o.order_id,
    bp.product_id,
    greatest(1, (random() * 5)::int),
    round((random() * 100)::numeric, 2)
FROM orders o
INNER JOIN branch_products bp
    ON o.branch_id = bp.branch_id
ORDER BY random()
LIMIT 15000;

-- ============================================
-- PAYMENTS
-- ============================================

INSERT INTO payments (
    order_id,
    amount,
    status
)
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

-- ============================================
-- SHIPMENTS
-- ============================================

INSERT INTO shipments (
    order_id,
    shipped_date,
    delivery_date,
    status
)
SELECT
    order_id,
    order_date + (random() * interval '3 days'),
    order_date + (random() * interval '10 days'),
    (
        ARRAY[
            'preparing',
            'shipped',
            'delivered'
        ]
    )[floor(random() * 3 + 1)]::shipment_status
FROM orders;

-- ============================================
-- 💥 BUSINESS ANOMALIES
-- ============================================

-- Paiement validé sur commande annulée
UPDATE payments
SET status = 'completed'
WHERE
    random() < 0.05
    AND order_id IN (
        SELECT order_id
        FROM orders
        WHERE status = 'cancelled'
    );

-- Livraison sans paiement validé
UPDATE shipments
SET status = 'delivered'
WHERE
    random() < 0.05
    AND order_id IN (
        SELECT order_id
        FROM payments
        WHERE status != 'completed'
    );

-- Stock négatif aggravé
UPDATE branch_products
SET stock = stock - 50
WHERE random() < 0.05;

-- Totaux incohérents
UPDATE orders
SET total_amount = total_amount * (random() * 3)
WHERE random() < 0.1;

-- Doublons emails
INSERT INTO users (
    email,
    password_hash,
    role
)
SELECT
    email,
    'hash',
    role
FROM users
WHERE
    email IS NOT NULL
    AND random() < 0.05;

-- Produits sans catégorie
DELETE FROM product_categories
WHERE random() < 0.03;

-- Clients sans ville
UPDATE customers
SET city = NULL
WHERE random() < 0.03;

-- Orders sans items
DELETE FROM order_items
WHERE order_id IN (
    SELECT order_id
    FROM orders
    WHERE random() < 0.02
);

-- Paiement supérieur au total
UPDATE payments
SET amount = amount * 5
WHERE random() < 0.02;

-- Livraison avant expédition
UPDATE shipments
SET delivery_date = shipped_date - interval '2 days'
WHERE random() < 0.01;

-- ============================================
-- ✅ CHECKS RAPIDES
-- ============================================

-- SELECT COUNT(*) FROM users;
-- SELECT COUNT(*) FROM customers;
-- SELECT COUNT(*) FROM products;
-- SELECT COUNT(*) FROM categories;
-- SELECT COUNT(*) FROM product_categories;
-- SELECT COUNT(*) FROM orders;
-- SELECT COUNT(*) FROM order_items;
-- SELECT COUNT(*) FROM payments;
-- SELECT COUNT(*) FROM shipments;