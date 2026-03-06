#!/usr/bin/env python3
"""
Seed data for DistroViz v3 database.
Provides comprehensive test data for plants, distribution centers, and orders.
"""

from datetime import datetime, date
from typing import Dict, List, Any


def get_seed_data() -> Dict[str, List[Dict[str, Any]]]:
    """Return comprehensive seed data for all tables."""
    
    plants_data = [
        {
            'name': 'North Manufacturing Plant',
            'location': 'Detroit, MI',
            'capacity': 50000,
            'is_active': True
        },
        {
            'name': 'South Production Facility',
            'location': 'Atlanta, GA',
            'capacity': 75000,
            'is_active': True
        },
        {
            'name': 'West Coast Operations',
            'location': 'Los Angeles, CA',
            'capacity': 60000,
            'is_active': True
        },
        {
            'name': 'Central Processing Hub',
            'location': 'Chicago, IL',
            'capacity': 80000,
            'is_active': True
        },
        {
            'name': 'East Coast Factory',
            'location': 'Boston, MA',
            'capacity': 45000,
            'is_active': True
        }
    ]
    
    distribution_centers_data = [
        {
            'name': 'Northeast Distribution Center',
            'region': 'Northeast',
            'storage_capacity': 100000,
            'is_active': True
        },
        {
            'name': 'Southeast Distribution Hub',
            'region': 'Southeast',
            'storage_capacity': 120000,
            'is_active': True
        },
        {
            'name': 'Midwest Logistics Center',
            'region': 'Midwest',
            'storage_capacity': 90000,
            'is_active': True
        },
        {
            'name': 'Southwest Distribution Point',
            'region': 'Southwest',
            'storage_capacity': 110000,
            'is_active': True
        },
        {
            'name': 'West Coast Warehouse',
            'region': 'West',
            'storage_capacity': 130000,
            'is_active': True
        },
        {
            'name': 'Central Distribution Facility',
            'region': 'Central',
            'storage_capacity': 95000,
            'is_active': True
        },
        {
            'name': 'Pacific Northwest Hub',
            'region': 'Northwest',
            'storage_capacity': 85000,
            'is_active': True
        },
        {
            'name': 'Mountain Region Center',
            'region': 'Mountain',
            'storage_capacity': 70000,
            'is_active': True
        }
    ]
    
    orders_data = [
        # January 2024 orders
        {
            'plant_id': 1, 'center_id': 1, 'quantity': 1500, 'status': 'delivered',
            'order_date': '2024-01-05', 'expected_delivery_date': '2024-01-12', 
            'actual_delivery_date': '2024-01-11', 'notes': 'Rush order completed ahead of schedule'
        },
        {
            'plant_id': 2, 'center_id': 2, 'quantity': 2200, 'status': 'delivered',
            'order_date': '2024-01-08', 'expected_delivery_date': '2024-01-15',
            'actual_delivery_date': '2024-01-16', 'notes': 'Slight delay due to weather conditions'
        },
        {
            'plant_id': 3, 'center_id': 5, 'quantity': 1800, 'status': 'delivered',
            'order_date': '2024-01-12', 'expected_delivery_date': '2024-01-19',
            'actual_delivery_date': '2024-01-18', 'notes': 'Standard delivery'
        },
        {
            'plant_id': 4, 'center_id': 3, 'quantity': 3000, 'status': 'delivered',
            'order_date': '2024-01-15', 'expected_delivery_date': '2024-01-22',
            'actual_delivery_date': '2024-01-21', 'notes': 'Large order processed efficiently'
        },
        {
            'plant_id': 5, 'center_id': 1, 'quantity': 1200, 'status': 'delivered',
            'order_date': '2024-01-18', 'expected_delivery_date': '2024-01-25',
            'actual_delivery_date': '2024-01-24', 'notes': 'Quality check passed'
        },
        
        # February 2024 orders
        {
            'plant_id': 1, 'center_id': 4, 'quantity': 2500, 'status': 'delivered',
            'order_date': '2024-02-02', 'expected_delivery_date': '2024-02-09',
            'actual_delivery_date': '2024-02-10', 'notes': 'Minor packaging delay'
        },
        {
            'plant_id': 3, 'center_id': 6, 'quantity': 1900, 'status': 'delivered',
            'order_date': '2024-02-05', 'expected_delivery_date': '2024-02-12',
            'actual_delivery_date': '2024-02-11', 'notes': 'Express shipping requested'
        },
        {
            'plant_id': 2, 'center_id': 7, 'quantity': 2800, 'status': 'delivered',
            'order_date': '2024-02-08', 'expected_delivery_date': '2024-02-15',
            'actual_delivery_date': '2024-02-14', 'notes': 'Bulk order for seasonal demand'
        },
        {
            'plant_id': 4, 'center_id': 8, 'quantity': 1600, 'status': 'delivered',
            'order_date': '2024-02-12', 'expected_delivery_date': '2024-02-19',
            'actual_delivery_date': '2024-02-20', 'notes': 'Remote location delivery'
        },
        {
            'plant_id': 5, 'center_id': 2, 'quantity': 2100, 'status': 'delivered',
            'order_date': '2024-02-15', 'expected_delivery_date': '2024-02-22',
            'actual_delivery_date': '2024-02-21', 'notes': 'Customer satisfaction high'
        },
        
        # March 2024 orders
        {
            'plant_id': 2, 'center_id': 3, 'quantity': 3200, 'status': 'delivered',
            'order_date': '2024-03-01', 'expected_delivery_date': '2024-03-08',
            'actual_delivery_date': '2024-03-07', 'notes': 'Peak season order'
        },
        {
            'plant_id': 1, 'center_id': 5, 'quantity': 1700, 'status': 'delivered',
            'order_date': '2024-03-05', 'expected_delivery_date': '2024-03-12',
            'actual_delivery_date': '2024-03-13', 'notes': 'Inventory restocking'
        },
        {
            'plant_id': 4, 'center_id': 1, 'quantity': 2400, 'status': 'delivered',
            'order_date': '2024-03-08', 'expected_delivery_date': '2024-03-15',
            'actual_delivery_date': '2024-03-14', 'notes': 'Priority customer order'
        },
        {
            'plant_id': 3, 'center_id': 4, 'quantity': 1950, 'status': 'delivered',
            'order_date': '2024-03-12', 'expected_delivery_date': '2024-03-19',
            'actual_delivery_date': '2024-03-18', 'notes': 'Standard processing time'
        },
        {
            'plant_id': 5, 'center_id': 6, 'quantity': 2700, 'status': 'delivered',
            'order_date': '2024-03-15', 'expected_delivery_date': '2024-03-22',
            'actual_delivery_date': '2024-03-23', 'notes': 'Delayed due to equipment maintenance'
        },
        
        # April 2024 orders
        {
            'plant_id': 1, 'center_id': 7, 'quantity': 1850, 'status': 'delivered',
            'order_date': '2024-04-02', 'expected_delivery_date': '2024-04-09',
            'actual_delivery_date': '2024-04-08', 'notes': 'Spring season preparation'
        },
        {
            'plant_id': 2, 'center_id': 8, 'quantity': 2300, 'status': 'delivered',
            'order_date': '2024-04-05', 'expected_delivery_date': '2024-04-12',
            'actual_delivery_date': '2024-04-11', 'notes': 'New product line launch'
        },
        {
            'plant_id': 4, 'center_id': 2, 'quantity': 2900, 'status': 'delivered',
            'order_date': '2024-04-08', 'expected_delivery_date': '2024-04-15',
            'actual_delivery_date': '2024-04-16', 'notes': 'High demand product'
        },
        {
            'plant_id': 3, 'center_id': 3, 'quantity': 1650, 'status': 'delivered',
            'order_date': '2024-04-12', 'expected_delivery_date': '2024-04-19',
            'actual_delivery_date': '2024-04-18', 'notes': 'Quality assurance completed'
        },
        {
            'plant_id': 5, 'center_id': 5, 'quantity': 2050, 'status': 'delivered',
            'order_date': '2024-04-15', 'expected_delivery_date': '2024-04-22',
            'actual_delivery_date': '2024-04-21', 'notes': 'Customer requested early delivery'
        },
        
        # May 2024 orders (recent delivered)
        {
            'plant_id': 2, 'center_id': 1, 'quantity': 2600, 'status': 'delivered',
            'order_date': '2024-05-01', 'expected_delivery_date': '2024-05-08',
            'actual_delivery_date': '2024-05-07', 'notes': 'Monthly restock order'
        },
        {
            'plant_id': 1, 'center_id': 4, 'quantity': 1750, 'status': 'delivered',
            'order_date': '2024-05-05', 'expected_delivery_date': '2024-05-12',
            'actual_delivery_date': '2024-05-11', 'notes': 'Promotional campaign support'
        },
        {
            'plant_id': 4, 'center_id': 6, 'quantity': 2200, 'status': 'delivered',
            'order_date': '2024-05-08', 'expected_delivery_date': '2024-05-15',
            'actual_delivery_date': '2024-05-14', 'notes': 'Regional expansion order'
        },
        
        # Current orders (May-June 2024)
        {
            'plant_id': 3, 'center_id': 7, 'quantity': 1900, 'status': 'shipped',
            'order_date': '2024-05-12', 'expected_delivery_date': '2024-05-19',
            'actual_delivery_date': None, 'notes': 'In transit to destination'
        },
        {
            'plant_id': 5, 'center_id': 8, 'quantity': 2400, 'status': 'shipped',
            'order_date': '2024-05-15', 'expected_delivery_date': '2024-05-22',
            'actual_delivery_date': None, 'notes': 'Tracking number provided'
        },
        {
            'plant_id': 1, 'center_id': 2, 'quantity': 1800, 'status': 'processing',
            'order_date': '2024-05-18', 'expected_delivery_date': '2024-05-25',
            'actual_delivery_date': None, 'notes': 'Currently in production queue'
        },
        {
            'plant_id': 2, 'center_id': 3, 'quantity': 2100, 'status': 'processing',
            'order_date': '2024-05-20', 'expected_delivery_date': '2024-05-27',
            'actual_delivery_date': None, 'notes': 'Awaiting quality control'
        },
        {
            'plant_id': 4, 'center_id': 5, 'quantity': 2800, 'status': 'pending',
            'order_date': '2024-05-22', 'expected_delivery_date': '2024-05-29',
            'actual_delivery_date': None, 'notes': 'Order received, pending approval'
        },
        {
            'plant_id': 3, 'center_id': 1, 'quantity': 1650, 'status': 'pending',
            'order_date': '2024-05-24', 'expected_delivery_date': '2024-05-31',
            'actual_delivery_date': None, 'notes': 'Waiting for production slot'
        },
        {
            'plant_id': 5, 'center_id': 4, 'quantity': 2300, 'status': 'pending',
            'order_date': '2024-05-26', 'expected_delivery_date': '2024-06-02',
            'actual_delivery_date': None, 'notes': 'New order, initial processing'
        }
    ]
    
    return {
        'plants': plants_data,
        'distribution_centers': distribution_centers_data,
        'orders': orders_data
    }


def get_plants_seed_data() -> List[Dict[str, Any]]:
    """Return only plants seed data."""
    return get_seed_data()['plants']


def get_distribution_centers_seed_data() -> List[Dict[str, Any]]:
    """Return only distribution centers seed data."""
    return get_seed_data()['distribution_centers']


def get_orders_seed_data() -> List[Dict[str, Any]]:
    """Return only orders seed data."""
    return get_seed_data()['orders']


def print_seed_data_summary():
    """Print summary of seed data for verification."""
    data = get_seed_data()
    
    print("Seed Data Summary:")
    print(f"  Plants: {len(data['plants'])}")
    print(f"  Distribution Centers: {len(data['distribution_centers'])}")
    print(f"  Orders: {len(data['orders'])}")
    
    # Order status breakdown
    orders = data['orders']
    status_counts = {}
    for order in orders:
        status = order['status']
        status_counts[status] = status_counts.get(status, 0) + 1
    
    print("\nOrder Status Breakdown:")
    for status, count in status_counts.items():
        print(f"  {status}: {count}")
    
    # Date range
    order_dates = [order['order_date'] for order in orders]
    print(f"\nOrder Date Range: {min(order_dates)} to {max(order_dates)}")


if __name__ == "__main__":
    print_seed_data_summary()
