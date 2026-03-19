from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal


# 📦 PRODUCT
class Product(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    brand = models.CharField(max_length=100, db_index=True)
    bike_model = models.CharField(max_length=100)
    category = models.CharField(max_length=100, db_index=True)
    part_number = models.CharField(max_length=100, unique=True, db_index=True)

    quantity = models.IntegerField(default=0)

    # 💰 SELLING PRICE
    price = models.DecimalField(max_digits=10, decimal_places=2)

    # 📉 COST PRICE
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    reorder_level = models.IntegerField(default=5)
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def is_low_stock(self):
        return self.quantity <= self.reorder_level

    @property
    def total_stock(self):
        return sum(stock.quantity for stock in self.stocks.all())

    @property
    def profit_per_item(self):
        return self.price - self.cost_price

    def __str__(self):
        return f"{self.name} ({self.part_number})"


# 🏬 WAREHOUSE
class Warehouse(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.name} - {self.location}"


# 📦 STOCK (🔥 AUTO ADD + SYNC WITH PRODUCT)
class Stock(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="stocks"
    )

    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE
    )

    quantity = models.IntegerField(default=0)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('product', 'warehouse')

    def save(self, *args, **kwargs):

        existing = Stock.objects.filter(
            product=self.product,
            warehouse=self.warehouse
        ).first()

        if existing and not self.pk:
            # 🔥 ADD quantity instead of duplicate error
            existing.quantity += self.quantity
            existing.save()

        else:
            super().save(*args, **kwargs)

        # 🔥 UPDATE PRODUCT TOTAL STOCK
        total = sum(s.quantity for s in Stock.objects.filter(product=self.product))
        self.product.quantity = total
        self.product.save()

    def __str__(self):
        return f"{self.product.name} - {self.warehouse.name} ({self.quantity})"


# 💰 SALE (🔥 REAL PROFIT SYSTEM)
class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        editable=False
    )

    profit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        editable=False,
        default=0
    )

    sold_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):

        self.total_price = self.product.price * self.quantity

        self.profit = (
            (self.product.price - self.product.cost_price)
            * self.quantity
        )

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Sale - {self.product.name} ({self.quantity})"


# 📦 ORDER (🔥 REFUND SYSTEM READY)
class Order(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('shipping', 'Shipping'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('returned', 'Returned'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    quantity = models.IntegerField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    # 🔄 REFUND FLAG
    is_refunded = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.price = self.product.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.id} - {self.product.name} ({self.status})"