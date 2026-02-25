from django.contrib import admin
from .models import Product, Sale, Warehouse, Stock


admin.site.register(Product)
admin.site.register(Sale)
admin.site.register(Warehouse)
admin.site.register(Stock)