from django.contrib import admin
from .models import Product, Stock, Order, Sale, Warehouse


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'category', 'quantity', 'price')
    search_fields = ('name', 'brand', 'part_number')
    list_filter = ('category', 'brand')


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('product', 'warehouse', 'quantity')
    list_filter = ('warehouse',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'quantity', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('product__name',)


admin.site.register(Sale)
admin.site.register(Warehouse)    