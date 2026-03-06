"""Seed database with demo data if empty."""
import logging
from datetime import date, timedelta
import random
from sqlalchemy import text
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

PLANTS = [
    {"name": "Planta Norte", "location": "Monterrey, NL", "capacity": 5000, "is_active": True},
    {"name": "Planta Sur", "location": "Mérida, YUC", "capacity": 3500, "is_active": True},
    {"name": "Planta Centro", "location": "Ciudad de México, CDMX", "capacity": 8000, "is_active": True},
    {"name": "Planta Occidente", "location": "Guadalajara, JAL", "capacity": 4500, "is_active": True},
    {"name": "Planta Oriente", "location": "Veracruz, VER", "capacity": 2800, "is_active": False},
]

CENTERS = [
    {"name": "CD Noreste", "region": "Noreste", "storage_capacity": 10000, "is_active": True},
    {"name": "CD Sureste", "region": "Sureste", "storage_capacity": 7500, "is_active": True},
    {"name": "CD Centro", "region": "Centro", "storage_capacity": 15000, "is_active": True},
    {"name": "CD Occidente", "region": "Occidente", "storage_capacity": 9000, "is_active": True},
    {"name": "CD Golfo", "region": "Golfo", "storage_capacity": 6000, "is_active": True},
    {"name": "CD Bajío", "region": "Bajío", "storage_capacity": 8500, "is_active": False},
]

STATUSES = ["pending", "processing", "shipped", "delivered", "delivered", "delivered", "cancelled"]


def seed_database(session: Session) -> None:
    """Populate the database with demo data if tables are empty."""
    count = session.execute(text("SELECT COUNT(*) FROM plants")).scalar()
    if count and count > 0:
        logger.info("Database already has data, skipping seed.")
        return

    logger.info("Seeding database with demo data...")

    # Insert plants
    for p in PLANTS:
        session.execute(
            text(
                "INSERT INTO plants (name, location, capacity, is_active) "
                "VALUES (:name, :location, :capacity, :is_active)"
            ),
            p,
        )
    session.commit()

    # Insert centers
    for c in CENTERS:
        session.execute(
            text(
                "INSERT INTO distribution_centers (name, region, storage_capacity, is_active) "
                "VALUES (:name, :region, :storage_capacity, :is_active)"
            ),
            c,
        )
    session.commit()

    # Get IDs
    plant_ids = [r[0] for r in session.execute(text("SELECT id FROM plants WHERE is_active = 1")).fetchall()]
    center_ids = [r[0] for r in session.execute(text("SELECT id FROM distribution_centers WHERE is_active = 1")).fetchall()]

    # Insert 60 orders spread over last 90 days
    today = date.today()
    random.seed(42)
    for i in range(60):
        order_date = today - timedelta(days=random.randint(0, 90))
        status = random.choice(STATUSES)
        expected = order_date + timedelta(days=random.randint(3, 14))
        actual = None
        if status == "delivered":
            actual = order_date + timedelta(days=random.randint(3, 12))

        session.execute(
            text(
                "INSERT INTO orders (plant_id, center_id, quantity, status, order_date, "
                "expected_delivery_date, actual_delivery_date) "
                "VALUES (:plant_id, :center_id, :quantity, :status, :order_date, "
                ":expected_delivery_date, :actual_delivery_date)"
            ),
            {
                "plant_id": random.choice(plant_ids),
                "center_id": random.choice(center_ids),
                "quantity": random.randint(100, 3000),
                "status": status,
                "order_date": order_date.isoformat(),
                "expected_delivery_date": expected.isoformat(),
                "actual_delivery_date": actual.isoformat() if actual else None,
            },
        )
    session.commit()
    logger.info("Seed data inserted: %d plants, %d centers, 60 orders.", len(PLANTS), len(CENTERS))
