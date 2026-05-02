-- =============================
-- TYPES (ENUMS)
-- =============================
CREATE TYPE user_role AS ENUM ('customer', 'admin');
CREATE TYPE order_status AS ENUM ('pending', 'paid', 'shipped', 'cancelled');
CREATE TYPE payment_status AS ENUM ('pending', 'completed', 'failed');
CREATE TYPE shipment_status AS ENUM ('preparing', 'shipped', 'delivered');

-- =============================
-- USERS
-- =============================
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    email TEXT, -- permissif
    password_hash TEXT,
    role user_role DEFAULT 'customer',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================
-- CUSTOMERS
-- =============================
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id) ON DELETE CASCADE, -- remove UNIQUE
    first_name TEXT,
    last_name TEXT,
    phone TEXT,
    address TEXT,
    city TEXT,
    country TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================
-- BRANCHES
-- =============================
CREATE TABLE branches (
    branch_id SERIAL PRIMARY KEY,
    name TEXT,
    city TEXT,
    country TEXT
);

-- =============================
-- PRODUCTS
-- =============================
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    name TEXT,
    description TEXT,
    price NUMERIC(10,2), -- remove NOT NULL
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================
-- STOCK
-- =============================
CREATE TABLE branch_products (
    branch_id INT REFERENCES branches(branch_id) ON DELETE CASCADE,
    product_id INT REFERENCES products(product_id) ON DELETE CASCADE,
    stock INT DEFAULT 0, -- remove CHECK
    PRIMARY KEY(branch_id, product_id)
);

-- =============================
-- CATEGORIES
-- =============================
CREATE TABLE categories (
    category_id SERIAL PRIMARY KEY,
    name TEXT
);

-- =============================
-- PRODUCT_CATEGORIES
-- =============================
CREATE TABLE product_categories (
    product_id INT REFERENCES products(product_id) ON DELETE CASCADE,
    category_id INT REFERENCES categories(category_id) ON DELETE CASCADE,
    PRIMARY KEY(product_id, category_id)
);

-- =============================
-- ORDERS
-- =============================
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(customer_id),
    branch_id INT REFERENCES branches(branch_id),
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status order_status DEFAULT 'pending',
    total_amount NUMERIC(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================
-- ORDER ITEMS
-- =============================
CREATE TABLE order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id INT REFERENCES orders(order_id) ON DELETE CASCADE,
    product_id INT REFERENCES products(product_id),
    quantity INT, -- remove CHECK
    price NUMERIC(10,2)
);

-- =============================
-- PAYMENTS
-- =============================
CREATE TABLE payments (
    payment_id SERIAL PRIMARY KEY,
    order_id INT REFERENCES orders(order_id) ON DELETE CASCADE,
    payment_method TEXT,
    amount NUMERIC(10,2),
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status payment_status DEFAULT 'pending'
);

-- =============================
-- SHIPMENTS
-- =============================
CREATE TABLE shipments (
    shipment_id SERIAL PRIMARY KEY,
    order_id INT REFERENCES orders(order_id) ON DELETE CASCADE,
    shipped_date TIMESTAMP,
    delivery_date TIMESTAMP,
    status shipment_status DEFAULT 'preparing'
);

-- =============================
-- INDEXES
-- =============================
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_orders_date ON orders(order_date);
CREATE INDEX idx_order_items_order_id ON order_items(order_id);
CREATE INDEX idx_products_created_at ON products(created_at);

-- =============================
-- ETL METADATA
-- =============================
CREATE TABLE etl_metadata (
    id SERIAL PRIMARY KEY,
    last_run TIMESTAMP
);