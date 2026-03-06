-- DistroViz v3 Initial Schema Migration
-- Migration: 001_initial_schema
-- Description: Create initial database schema with plants, distribution_centers, and orders tables
-- Created: 2024-05-27

-- Enable SQLite features
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA cache_size = 1000;
PRAGMA temp_store = MEMORY;

-- Migration UP: Create tables and indexes
-- Plants table
CREATE TABLE IF NOT EXISTS plants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    location VARCHAR(255) NOT NULL,
    capacity INTEGER NOT NULL CHECK (capacity > 0),
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME
);

-- Create indexes for plants table
CREATE INDEX IF NOT EXISTS idx_plants_name ON plants(name);
CREATE INDEX IF NOT EXISTS idx_plants_location ON plants(location);
CREATE INDEX IF NOT EXISTS idx_plants_is_active ON plants(is_active);
CREATE INDEX IF NOT EXISTS idx_plants_created_at ON plants(created_at);

-- Distribution Centers table
CREATE TABLE IF NOT EXISTS distribution_centers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    region VARCHAR(255) NOT NULL,
    storage_capacity INTEGER NOT NULL CHECK (storage_capacity > 0),
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME
);

-- Create indexes for distribution_centers table
CREATE INDEX IF NOT EXISTS idx_distribution_centers_name ON distribution_centers(name);
CREATE INDEX IF NOT EXISTS idx_distribution_centers_region ON distribution_centers(region);
CREATE INDEX IF NOT EXISTS idx_distribution_centers_is_active ON distribution_centers(is_active);
CREATE INDEX IF NOT EXISTS idx_distribution_centers_created_at ON distribution_centers(created_at);

-- Orders table
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plant_id INTEGER NOT NULL,
    center_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    status VARCHAR(50) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'shipped', 'delivered', 'cancelled')),
    order_date DATE NOT NULL,
    expected_delivery_date DATE,
    actual_delivery_date DATE,
    notes TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME,
    FOREIGN KEY (plant_id) REFERENCES plants(id) ON DELETE CASCADE,
    FOREIGN KEY (center_id) REFERENCES distribution_centers(id) ON DELETE CASCADE,
    CHECK (expected_delivery_date IS NULL OR expected_delivery_date >= order_date),
    CHECK (actual_delivery_date IS NULL OR actual_delivery_date >= order_date)
);

-- Create indexes for orders table
CREATE INDEX IF NOT EXISTS idx_orders_plant_id ON orders(plant_id);
CREATE INDEX IF NOT EXISTS idx_orders_center_id ON orders(center_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_order_date ON orders(order_date);
CREATE INDEX IF NOT EXISTS idx_orders_expected_delivery_date ON orders(expected_delivery_date);
CREATE INDEX IF NOT EXISTS idx_orders_actual_delivery_date ON orders(actual_delivery_date);
CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at);

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_orders_plant_status ON orders(plant_id, status);
CREATE INDEX IF NOT EXISTS idx_orders_center_status ON orders(center_id, status);
CREATE INDEX IF NOT EXISTS idx_orders_date_status ON orders(order_date, status);

-- Create a view for order statistics (useful for dashboard queries)
CREATE VIEW IF NOT EXISTS order_statistics AS
SELECT 
    COUNT(*) as total_orders,
    COUNT(CASE WHEN status = 'delivered' THEN 1 END) as delivered_orders,
    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_orders,
    COUNT(CASE WHEN status = 'processing' THEN 1 END) as processing_orders,
    COUNT(CASE WHEN status = 'shipped' THEN 1 END) as shipped_orders,
    COUNT(CASE WHEN status = 'cancelled' THEN 1 END) as cancelled_orders,
    ROUND(AVG(CASE 
        WHEN status = 'delivered' AND actual_delivery_date IS NOT NULL AND order_date IS NOT NULL 
        THEN julianday(actual_delivery_date) - julianday(order_date)
        ELSE NULL 
    END), 2) as avg_delivery_days,
    ROUND(
        (COUNT(CASE WHEN status = 'delivered' THEN 1 END) * 100.0) / 
        NULLIF(COUNT(CASE WHEN status IN ('delivered', 'cancelled') THEN 1 END), 0), 
        2
    ) as fulfillment_rate_percent
FROM orders;

-- Create view for monthly order trends
CREATE VIEW IF NOT EXISTS monthly_order_trends AS
SELECT 
    strftime('%Y-%m', order_date) as month,
    COUNT(*) as order_count,
    SUM(quantity) as total_quantity,
    COUNT(CASE WHEN status = 'delivered' THEN 1 END) as delivered_count,
    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_count,
    COUNT(CASE WHEN status = 'processing' THEN 1 END) as processing_count,
    COUNT(CASE WHEN status = 'shipped' THEN 1 END) as shipped_count,
    COUNT(CASE WHEN status = 'cancelled' THEN 1 END) as cancelled_count
FROM orders
GROUP BY strftime('%Y-%m', order_date)
ORDER BY month;

-- Create view for plant performance
CREATE VIEW IF NOT EXISTS plant_performance AS
SELECT 
    p.id,
    p.name,
    p.location,
    p.capacity,
    COUNT(o.id) as total_orders,
    SUM(o.quantity) as total_quantity,
    COUNT(CASE WHEN o.status = 'delivered' THEN 1 END) as delivered_orders,
    ROUND(
        (COUNT(CASE WHEN o.status = 'delivered' THEN 1 END) * 100.0) / 
        NULLIF(COUNT(o.id), 0), 
        2
    ) as delivery_success_rate
FROM plants p
LEFT JOIN orders o ON p.id = o.plant_id
WHERE p.is_active = 1
GROUP BY p.id, p.name, p.location, p.capacity;

-- Create view for distribution center performance
CREATE VIEW IF NOT EXISTS center_performance AS
SELECT 
    dc.id,
    dc.name,
    dc.region,
    dc.storage_capacity,
    COUNT(o.id) as total_orders,
    SUM(o.quantity) as total_quantity,
    COUNT(CASE WHEN o.status = 'delivered' THEN 1 END) as delivered_orders,
    ROUND(
        (COUNT(CASE WHEN o.status = 'delivered' THEN 1 END) * 100.0) / 
        NULLIF(COUNT(o.id), 0), 
        2
    ) as delivery_success_rate
FROM distribution_centers dc
LEFT JOIN orders o ON dc.id = o.center_id
WHERE dc.is_active = 1
GROUP BY dc.id, dc.name, dc.region, dc.storage_capacity;

-- Migration metadata (for tracking)
CREATE TABLE IF NOT EXISTS schema_migrations (
    version VARCHAR(255) PRIMARY KEY,
    applied_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

-- Record this migration
INSERT OR REPLACE INTO schema_migrations (version, description) 
VALUES ('001_initial_schema', 'Create initial database schema with plants, distribution_centers, and orders tables');

-- Migration DOWN (for rollback - commented out for safety)
-- To rollback this migration, uncomment and run the following:
/*
DROP VIEW IF EXISTS center_performance;
DROP VIEW IF EXISTS plant_performance;
DROP VIEW IF EXISTS monthly_order_trends;
DROP VIEW IF EXISTS order_statistics;

DROP INDEX IF EXISTS idx_orders_date_status;
DROP INDEX IF EXISTS idx_orders_center_status;
DROP INDEX IF EXISTS idx_orders_plant_status;
DROP INDEX IF EXISTS idx_orders_created_at;
DROP INDEX IF EXISTS idx_orders_actual_delivery_date;
DROP INDEX IF EXISTS idx_orders_expected_delivery_date;
DROP INDEX IF EXISTS idx_orders_order_date;
DROP INDEX IF EXISTS idx_orders_status;
DROP INDEX IF EXISTS idx_orders_center_id;
DROP INDEX IF EXISTS idx_orders_plant_id;

DROP INDEX IF EXISTS idx_distribution_centers_created_at;
DROP INDEX IF EXISTS idx_distribution_centers_is_active;
DROP INDEX IF EXISTS idx_distribution_centers_region;
DROP INDEX IF EXISTS idx_distribution_centers_name;

DROP INDEX IF EXISTS idx_plants_created_at;
DROP INDEX IF EXISTS idx_plants_is_active;
DROP INDEX IF EXISTS idx_plants_location;
DROP INDEX IF EXISTS idx_plants_name;

DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS distribution_centers;
DROP TABLE IF EXISTS plants;
DROP TABLE IF EXISTS schema_migrations;
*/
