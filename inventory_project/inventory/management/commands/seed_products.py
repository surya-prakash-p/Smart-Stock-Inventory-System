from django.core.management.base import BaseCommand
from inventory.models import Product


class Command(BaseCommand):
    help = "Seed bike spare products"

    def handle(self, *args, **kwargs):
        products = [
            {
                "name": "Brake Pad Set",
                "brand": "TVS",
                "bike_model": "Apache RTR 160",
                "category": "Brake System",
                "part_number": "BP-AP160-001",
                "quantity": 0,
                "price": 450.00,
                "reorder_level": 5,
                "description": "High-quality front brake pad set compatible with TVS Apache RTR 160. Provides smooth braking and long life."
            },
            {
                "name": "Spark Plug",
                "brand": "NGK",
                "bike_model": "Hero Splendor Plus",
                "category": "Engine Parts",
                "part_number": "SP-HSPL-002",
                "quantity": 0,
                "price": 120.00,
                "reorder_level": 10,
                "description": "Genuine NGK spark plug suitable for Hero Splendor Plus. Ensures efficient combustion and mileage."
            },
            {
                "name": "Bike Battery 12V",
                "brand": "Amaron",
                "bike_model": "Bajaj Pulsar 150",
                "category": "Electrical",
                "part_number": "BAT-PL150-003",
                "quantity": 0,
                "price": 1850.00,
                "reorder_level": 3,
                "description": "Maintenance-free 12V battery designed for Bajaj Pulsar 150 with high cranking power."
            },
            {
                "name": "Clutch Cable",
                "brand": "Bajaj Genuine",
                "bike_model": "Bajaj CT 100",
                "category": "Control Cables",
                "part_number": "CC-CT100-004",
                "quantity": 0,
                "price": 95.00,
                "reorder_level": 10,
                "description": "Durable clutch cable for smooth clutch operation in Bajaj CT 100."
            },
            {
                "name": "Front Disc Brake",
                "brand": "Yamaha",
                "bike_model": "Yamaha FZ V3",
                "category": "Brake System",
                "part_number": "DB-FZV3-005",
                "quantity": 0,
                "price": 2200.00,
                "reorder_level": 2,
                "description": "OEM front disc brake rotor compatible with Yamaha FZ V3 for superior stopping performance."
            },
            {
                "name": "Headlight Assembly",
                "brand": "Honda",
                "bike_model": "Honda Shine",
                "category": "Electrical",
                "part_number": "HL-HSH-006",
                "quantity": 0,
                "price": 1350.00,
                "reorder_level": 5,
                "description": "Complete headlight assembly unit suitable for Honda Shine with clear visibility."
            },
            {
                "name": "Chain Sprocket Kit",
                "brand": "Rolon",
                "bike_model": "Hero HF Deluxe",
                "category": "Transmission",
                "part_number": "CS-HFD-007",
                "quantity": 0,
                "price": 950.00,
                "reorder_level": 4,
                "description": "High-strength chain sprocket kit for Hero HF Deluxe ensuring smooth power transmission."
            },
            {
                "name": "Side Mirror Set",
                "brand": "Universal",
                "bike_model": "Universal Fit",
                "category": "Body Parts",
                "part_number": "SM-UNI-008",
                "quantity": 0,
                "price": 180.00,
                "reorder_level": 15,
                "description": "Universal rear view side mirror set compatible with most commuter bikes."
            },
        ]

        created_count = 0

        for p in products:
            obj, created = Product.objects.get_or_create(
                part_number=p["part_number"],
                defaults=p
            )
            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f"✅ {created_count} products inserted/verified")
        )