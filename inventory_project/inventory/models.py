from django.db import models

from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=200)
    brand = models.CharField(max_length=100)
    bike_model = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    part_number = models.CharField(max_length=100, unique=True)
    quantity = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    reorder_level = models.IntegerField(default=5)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_low_stock(self):
        return self.quantity <= self.reorder_level

    def __str__(self):
        return f"{self.name} ({self.part_number})"
    
class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    sold_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sale - {self.product.name}"