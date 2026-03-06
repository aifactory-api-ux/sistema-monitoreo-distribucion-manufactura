-- DistroViz v3 Database Schema
-- SQLite database with foreign key constraints and indexes

-- Enable foreign key constraints
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA cache_size = 1000;
PRAGMA temp_store = MEMORY;

-- Drop tables if they exist (for clean setup)
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS distribution_centers;
DROP TABLE IF EXISTS plants;

-- Plants table
CREATE TABLE plants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    location VARCHAR(255) NOT NULL,
    capacity INTEGER NOT NULL CHECK (capacity > 0),
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME
);

-- Create indexes for plants table
CREATE INDEX idx_plants_name ON plants(name);
CREATE INDEX idx_plants_location ON plants(location);
CREATE INDEX idx_plants_is_active ON plants(is_active);
CREATE INDEX idx_plants_created_at ON plants(created_at);

-- Distribution Centers table
CREATE TABLE distribution_centers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    region VARCHAR(255) NOT NULL,
    storage_capacity INTEGER NOT NULL CHECK (storage_capacity > 0),
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME
);

-- Create indexes for distribution_centers table
CREATE INDEX idx_distribution_centers_name ON distribution_centers(name);
CREATE INDEX idx_distribution_centers_region ON distribution_centers(region);
CREATE INDEX idx_distribution_centers_is_active ON distribution_centers(is_active);
CREATE INDEX idx_distribution_centers_created_at ON distribution_centers(created_at);

-- Orders table
CREATE TABLE orders (
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
CREATE INDEX idx_orders_plant_id ON orders(plant_id);
CREATE INDEX idx_orders_center_id ON orders(center_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_order_date ON orders(order_date);
CREATE INDEX idx_orders_expected_delivery_date ON orders(expected_delivery_date);
CREATE INDEX idx_orders_actual_delivery_date ON orders(actual_delivery_date);
CREATE INDEX idx_orders_created_at ON orders(created_at);

-- Composite indexes for common queries
CREATE INDEX idx_orders_plant_status ON orders(plant_id, status);
CREATE INDEX idx_orders_center_status ON orders(center_id, status);
CREATE INDEX idx_orders_date_status ON orders(order_date, status);

-- Insert seed data for plants
INSERT INTO plants (name, location, capacity, is_active) VALUES
('North Manufacturing Plant', 'Detroit, MI', 50000, 1),
('South Production Facility', 'Atlanta, GA', 75000, 1),
('West Coast Operations', 'Los Angeles, CA', 60000, 1),
('Central Processing Hub', 'Chicago, IL', 80000, 1),
('East Coast Factory', 'Boston, MA', 45000, 1);

-- Insert seed data for distribution centers
INSERT INTO distribution_centers (name, region, storage_capacity, is_active) VALUES
('Northeast Distribution Center', 'Northeast', 100000, 1),
('Southeast Distribution Hub', 'Southeast', 120000, 1),
('Midwest Logistics Center', 'Midwest', 90000, 1),
('Southwest Distribution Point', 'Southwest', 110000, 1),
('West Coast Warehouse', 'West', 130000, 1),
('Central Distribution Facility', 'Central', 95000, 1),
('Pacific Northwest Hub', 'Northwest', 85000, 1),
('Mountain Region Center', 'Mountain', 70000, 1);

-- Insert seed data for orders (30 historical orders with realistic data)
INSERT INTO orders (plant_id, center_id, quantity, status, order_date, expected_delivery_date, actual_delivery_date, notes) VALUES
-- January 2024 orders
(1, 1, 1500, 'delivered', '2024-01-05', '2024-01-12', '2024-01-11', 'Rush order completed ahead of schedule'),
(2, 2, 2200, 'delivered', '2024-01-08', '2024-01-15', '2024-01-16', 'Slight delay due to weather conditions'),
(3, 5, 1800, 'delivered', '2024-01-12', '2024-01-19', '2024-01-18', 'Standard delivery'),
(4, 3, 3000, 'delivered', '2024-01-15', '2024-01-22', '2024-01-21', 'Large order processed efficiently'),
(5, 1, 1200, 'delivered', '2024-01-18', '2024-01-25', '2024-01-24', 'Quality check passed'),

-- February 2024 orders
(1, 4, 2500, 'delivered', '2024-02-02', '2024-02-09', '2024-02-10', 'Minor packaging delay'),
(3, 6, 1900, 'delivered', '2024-02-05', '2024-02-12', '2024-02-11', 'Express shipping requested'),
(2, 7, 2800, 'delivered', '2024-02-08', '2024-02-15', '2024-02-14', 'Bulk order for seasonal demand'),
(4, 8, 1600, 'delivered', '2024-02-12', '2024-02-19', '2024-02-20', 'Remote location delivery'),
(5, 2, 2100, 'delivered', '2024-02-15', '2024-02-22', '2024-02-21', 'Customer satisfaction high'),

-- March 2024 orders
(2, 3, 3200, 'delivered', '2024-03-01', '2024-03-08', '2024-03-07', 'Peak season order'),
(1, 5, 1700, 'delivered', '2024-03-05', '2024-03-12', '2024-03-13', 'Inventory restocking'),
(4, 1, 2400, 'delivered', '2024-03-08', '2024-03-15', '2024-03-14', 'Priority customer order'),
(3, 4, 1950, 'delivered', '2024-03-12', '2024-03-19', '2024-03-18', 'Standard processing time'),
(5, 6, 2700, 'delivered', '2024-03-15', '2024-03-22', '2024-03-23', 'Delayed due to equipment maintenance'),

-- April 2024 orders
(1, 7, 1850, 'delivered', '2024-04-02', '2024-04-09', '2024-04-08', 'Spring season preparation'),
(2, 8, 2300, 'delivered', '2024-04-05', '2024-04-12', '2024-04-11', 'New product line launch'),
(4, 2, 2900, 'delivered', '2024-04-08', '2024-04-15', '2024-04-16', 'High demand product'),
(3, 3, 1650, 'delivered', '2024-04-12', '2024-04-19', '2024-04-18', 'Quality assurance completed'),
(5, 5, 2050, 'delivered', '2024-04-15', '2024-04-22', '2024-04-21', 'Customer requested early delivery'),

-- May 2024 orders (recent delivered)
(2, 1, 2600, 'delivered', '2024-05-01', '2024-05-08', '2024-05-07', 'Monthly restock order'),
(1, 4, 1750, 'delivered', '2024-05-05', '2024-05-12', '2024-05-11', 'Promotional campaign support'),
(4, 6, 2200, 'delivered', '2024-05-08', '2024-05-15', '2024-05-14', 'Regional expansion order'),

-- Current orders (May-June 2024)
(3, 7, 1900, 'shipped', '2024-05-12', '2024-05-19', NULL, 'In transit to destination'),
(5, 8, 2400, 'shipped', '2024-05-15', '2024-05-22', NULL, 'Tracking number provided'),
(1, 2, 1800, 'processing', '2024-05-18', '2024-05-25', NULL, 'Currently in production queue'),
(2, 3, 2100, 'processing', '2024-05-20', '2024-05-27', NULL, 'Awaiting quality control'),
(4, 5, 2800, 'pending', '2024-05-22', '2024-05-29', NULL, 'Order received, pending approval'),
(3, 1, 1650, 'pending', '2024-05-24', '2024-05-31', NULL, 'Waiting for production slot'),
(5, 4, 2300, 'pending', '2024-05-26', '2024-06-02', NULL, 'New order, initial processing');

-- Create a view for order statistics (useful for dashboard queries)
CREATE VIEW order_statistics AS
SELECT 
    COUNT(*) as total_orders,
    COUNT(CASE WHEN status = 'delivered' THEN 1 END) as delivered_orders,
    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_orders,
    COUNT(CASE WHEN status = 'processing' THEN 1 END) as processing_orders,
    COUNT(CASE WHEN status = 'shipped' THEN 1 END) as shipped_orders,
    COUNT(CASE WHEN status = 'cancelled' THEN 1 END) as cancelled_orders,
    ROUND(
        (COUNT(CASE WHEN status = 'delivered' THEN 1 END) * 100.0 / COUNT(*)), 2
    ) as fulfillment_rate,
    ROUND(
        AVG(
            CASE 
                WHEN status = 'delivered' AND actual_delivery_date IS NOT NULL 
                THEN julianday(actual_delivery_date) - julianday(order_date)
                ELSE NULL 
            END
        ), 2
    ) as avg_delivery_days
FROM orders;

-- Create a view for monthly order trends
CREATE VIEW monthly_order_trends AS
SELECT 
    strftime('%Y-%m', order_date) as month,
    COUNT(*) as order_count,
    SUM(quantity) as total_quantity,
    COUNT(CASE WHEN status = 'delivered' THEN 1 END) as delivered_count
FROM orders
GROUP BY strftime('%Y-%m', order_date)
ORDER BY month;

-- Verify the data was inserted correctly
-- SELECT 'Plants count: ' || COUNT(*) FROM plants;
-- SELECT 'Distribution centers count: ' || COUNT(*) FROM distribution_centers;
-- SELECT 'Orders count: ' || COUNT(*) FROM orders;
-- SELECT * FROM order_statistics;

-- Create triggers for updated_at timestamps
CREATE TRIGGER update_plants_timestamp 
    AFTER UPDATE ON plants
    FOR EACH ROW
    WHEN NEW.updated_at IS NULL OR NEW.updated_at = OLD.updated_at
BEGIN
    UPDATE plants SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER update_distribution_centers_timestamp 
    AFTER UPDATE ON distribution_centers
    FOR EACH ROW
    WHEN NEW.updated_at IS NULL OR NEW.updated_at = OLD.updated_at
BEGIN
    UPDATE distribution_centers SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER update_orders_timestamp 
    AFTER UPDATE ON orders
    FOR EACH ROW
    WHEN NEW.updated_at IS NULL OR NEW.updated_at = OLD.updated_at
BEGIN
    UPDATE orders SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Final verification queries (commented out for production)
-- SELECT 'Database schema created successfully' as status;
-- SELECT COUNT(*) as plant_count FROM plants;
-- SELECT COUNT(*) as center_count FROM distribution_centers;
-- SELECT COUNT(*) as order_count FROM orders;
-- SELECT status, COUNT(*) as count FROM orders GROUP BY status;