from django.core.management.base import BaseCommand
from inventory.models import Product, Warehouse, Stock


class Command(BaseCommand):
    help = "Seed warehouse and stock data"

    def handle(self, *args, **kwargs):

        # ✅ Create warehouses
        chennai, _ = Warehouse.objects.get_or_create(
            name="Chennai Warehouse",
            defaults={"location": "Chennai"}
        )

        madurai, _ = Warehouse.objects.get_or_create(
            name="Madurai Warehouse",
            defaults={"location": "Madurai"}
        )

        self.stdout.write(self.style.SUCCESS("✅ Warehouses ready"))

        # ✅ Create stock for each product
        for product in Product.objects.all():

            Stock.objects.update_or_create(
                product=product,
                warehouse=chennai,
                defaults={"quantity": 10}
            )

            Stock.objects.update_or_create(
                product=product,
                warehouse=madurai,
                defaults={"quantity": 5}
            )

        self.stdout.write(self.style.SUCCESS("✅ Warehouse stock seeded"))