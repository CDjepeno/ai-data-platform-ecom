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
    user_id serial PRIMARY KEY,
    email text,
    password_hash text,
    role user_role DEFAULT 'customer',
    created_at timestamp DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp DEFAULT CURRENT_TIMESTAMP
);

-- =============================
-- CUSTOMERS
-- =============================
CREATE TABLE customers (
    customer_id serial PRIMARY KEY,
    user_id int REFERENCES users (user_id) ON DELETE CASCADE,
    first_name text,
    last_name text,
    phone text,
    address text,
    city text,
    country text,
    created_at timestamp DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp DEFAULT CURRENT_TIMESTAMP
);

-- =============================
-- BRANCHES
-- =============================
CREATE TABLE branches (
    branch_id serial PRIMARY KEY,
    name text,
    city text,
    country text,
    created_at timestamp DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp DEFAULT CURRENT_TIMESTAMP
);

-- =============================
-- PRODUCTS
-- =============================
CREATE TABLE products (
    product_id serial PRIMARY KEY,
    name text,
    description text,
    price numeric(10, 2),
    created_at timestamp DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp DEFAULT CURRENT_TIMESTAMP
);

-- =============================
-- STOCK
-- =============================
CREATE TABLE branch_products (
    branch_id int REFERENCES branches (branch_id) ON DELETE CASCADE,
    product_id int REFERENCES products (product_id) ON DELETE CASCADE,
    stock int DEFAULT 0,
    created_at timestamp DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (branch_id, product_id)
);

-- =============================
-- CATEGORIES
-- =============================
CREATE TABLE categories (
    category_id serial PRIMARY KEY,
    name text,
    created_at timestamp DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp DEFAULT CURRENT_TIMESTAMP
);

-- =============================
-- PRODUCT_CATEGORIES
-- =============================
CREATE TABLE product_categories (
    product_id int REFERENCES products (product_id) ON DELETE CASCADE,
    category_id int REFERENCES categories (category_id) ON DELETE CASCADE,
    created_at timestamp DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (product_id, category_id)
);

-- =============================
-- ORDERS
-- =============================
CREATE TABLE orders (
    order_id serial PRIMARY KEY,
    customer_id int REFERENCES customers (customer_id),
    branch_id int REFERENCES branches (branch_id),
    order_date timestamp DEFAULT CURRENT_TIMESTAMP,
    status order_status DEFAULT 'pending',
    total_amount numeric(10, 2),
    created_at timestamp DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp DEFAULT CURRENT_TIMESTAMP
);

-- =============================
-- ORDER ITEMS
-- =============================
CREATE TABLE order_items (
    order_item_id serial PRIMARY KEY,
    order_id int REFERENCES orders (order_id) ON DELETE CASCADE,
    product_id int REFERENCES products (product_id),
    quantity int,
    price numeric(10, 2),
    created_at timestamp DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp DEFAULT CURRENT_TIMESTAMP
);

-- =============================
-- PAYMENTS
-- =============================
CREATE TABLE payments (
    payment_id serial PRIMARY KEY,
    order_id int REFERENCES orders (order_id) ON DELETE CASCADE,
    payment_method text,
    amount numeric(10, 2),
    payment_date timestamp DEFAULT CURRENT_TIMESTAMP,
    status payment_status DEFAULT 'pending',
    created_at timestamp DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp DEFAULT CURRENT_TIMESTAMP
);

-- =============================
-- SHIPMENTS
-- =============================
CREATE TABLE shipments (
    shipment_id serial PRIMARY KEY,
    order_id int REFERENCES orders (order_id) ON DELETE CASCADE,
    shipped_date timestamp,
    delivery_date timestamp,
    status shipment_status DEFAULT 'preparing',
    created_at timestamp DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp DEFAULT CURRENT_TIMESTAMP
);

-- =============================
-- INDEXES
-- =============================
CREATE INDEX idx_orders_customer_id ON orders (customer_id);
CREATE INDEX idx_orders_date ON orders (order_date);
CREATE INDEX idx_order_items_order_id ON order_items (order_id);
CREATE INDEX idx_products_created_at ON products (created_at);