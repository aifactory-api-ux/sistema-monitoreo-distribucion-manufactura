#!/usr/bin/env python3
"""
Database initialization script for DistroViz v3.
Creates SQLite database with tables, indexes, and seed data.
"""

import os
import sqlite3
import sys
from pathlib import Path
from typing import Optional

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.db.seed_data import get_seed_data


class DatabaseInitializer:
    """Handles SQLite database initialization with schema and seed data."""
    
    def __init__(self, db_path: str = "distroviz.db"):
        self.db_path = db_path
        self.schema_path = Path(__file__).parent / "schema.sql"
        
    def create_database(self) -> None:
        """Create database file and execute schema SQL."""
        try:
            # Remove existing database if it exists
            if os.path.exists(self.db_path):
                os.remove(self.db_path)
                print(f"Removed existing database: {self.db_path}")
            
            # Create new database connection
            conn = sqlite3.connect(self.db_path)
            conn.execute("PRAGMA foreign_keys = ON")
            
            # Read and execute schema SQL
            if not self.schema_path.exists():
                raise FileNotFoundError(f"Schema file not found: {self.schema_path}")
                
            with open(self.schema_path, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            
            # Execute schema in chunks (split by semicolon)
            statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
            
            for statement in statements:
                if statement:
                    try:
                        conn.execute(statement)
                    except sqlite3.Error as e:
                        print(f"Warning: Error executing statement: {e}")
                        print(f"Statement: {statement[:100]}...")
            
            conn.commit()
            conn.close()
            
            print(f"Database created successfully: {self.db_path}")
            
        except Exception as e:
            print(f"Error creating database: {e}")
            raise
    
    def insert_seed_data(self) -> None:
        """Insert seed data into the database."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("PRAGMA foreign_keys = ON")
            cursor = conn.cursor()
            
            seed_data = get_seed_data()
            
            # Insert plants
            print("Inserting plant data...")
            for plant in seed_data['plants']:
                cursor.execute(
                    "INSERT INTO plants (name, location, capacity, is_active) VALUES (?, ?, ?, ?)",
                    (plant['name'], plant['location'], plant['capacity'], plant['is_active'])
                )
            
            # Insert distribution centers
            print("Inserting distribution center data...")
            for center in seed_data['distribution_centers']:
                cursor.execute(
                    "INSERT INTO distribution_centers (name, region, storage_capacity, is_active) VALUES (?, ?, ?, ?)",
                    (center['name'], center['region'], center['storage_capacity'], center['is_active'])
                )
            
            # Insert orders
            print("Inserting order data...")
            for order in seed_data['orders']:
                cursor.execute(
                    """INSERT INTO orders 
                       (plant_id, center_id, quantity, status, order_date, expected_delivery_date, actual_delivery_date, notes) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        order['plant_id'], order['center_id'], order['quantity'], order['status'],
                        order['order_date'], order['expected_delivery_date'], 
                        order['actual_delivery_date'], order['notes']
                    )
                )
            
            conn.commit()
            
            # Verify data insertion
            cursor.execute("SELECT COUNT(*) FROM plants")
            plant_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM distribution_centers")
            center_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM orders")
            order_count = cursor.fetchone()[0]
            
            conn.close()
            
            print(f"Seed data inserted successfully:")
            print(f"  - Plants: {plant_count}")
            print(f"  - Distribution Centers: {center_count}")
            print(f"  - Orders: {order_count}")
            
        except Exception as e:
            print(f"Error inserting seed data: {e}")
            raise
    
    def verify_database(self) -> bool:
        """Verify database structure and data integrity."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if all tables exist
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('plants', 'distribution_centers', 'orders')"
            )
            tables = [row[0] for row in cursor.fetchall()]
            
            expected_tables = ['plants', 'distribution_centers', 'orders']
            missing_tables = set(expected_tables) - set(tables)
            
            if missing_tables:
                print(f"Missing tables: {missing_tables}")
                return False
            
            # Check foreign key constraints
            cursor.execute("PRAGMA foreign_key_check")
            fk_violations = cursor.fetchall()
            
            if fk_violations:
                print(f"Foreign key violations found: {fk_violations}")
                return False
            
            # Check data counts
            cursor.execute("SELECT COUNT(*) FROM plants WHERE is_active = 1")
            active_plants = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM distribution_centers WHERE is_active = 1")
            active_centers = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM orders")
            total_orders = cursor.fetchone()[0]
            
            conn.close()
            
            print(f"Database verification successful:")
            print(f"  - Active plants: {active_plants}")
            print(f"  - Active distribution centers: {active_centers}")
            print(f"  - Total orders: {total_orders}")
            
            return True
            
        except Exception as e:
            print(f"Error verifying database: {e}")
            return False
    
    def initialize(self) -> bool:
        """Complete database initialization process."""
        try:
            print("Starting database initialization...")
            
            # Create database and schema
            self.create_database()
            
            # Insert seed data
            self.insert_seed_data()
            
            # Verify everything is correct
            if not self.verify_database():
                raise Exception("Database verification failed")
            
            print(f"\nDatabase initialization completed successfully!")
            print(f"Database file: {os.path.abspath(self.db_path)}")
            
            return True
            
        except Exception as e:
            print(f"Database initialization failed: {e}")
            return False


def main():
    """Main entry point for database initialization."""
    # Change to project root directory
    os.chdir(project_root)
    
    # Initialize database
    initializer = DatabaseInitializer()
    
    success = initializer.initialize()
    
    if not success:
        sys.exit(1)
    
    print("\nTo verify the database, run:")
    print('sqlite3 distroviz.db "SELECT COUNT(*) FROM orders"')


if __name__ == "__main__":
    main()
