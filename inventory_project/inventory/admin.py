from django.contrib import admin
from .models import Product, Sale, Warehouse, Stock, Order


admin.site.register(Product)
admin.site.register(Sale)
admin.site.register(Warehouse)
admin.site.register(Stock)
admin.site.register(Order)