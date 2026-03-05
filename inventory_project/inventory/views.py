from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum, F
from .models import Product, Sale, Stock, Warehouse, Order
from datetime import timedelta
from django.utils import timezone


# 🏠 HOME
def home(request):
    query = request.GET.get('q')

    if query:
        products = Product.objects.filter(name__icontains=query)
    else:
        products = Product.objects.all()

    return render(request, 'inventory/home.html', {
        'products': products
    })


# 🛒 ADD TO CART
def add_to_cart(request, id):
    cart = request.session.get('cart', {})
    cart[str(id)] = cart.get(str(id), 0) + 1
    request.session['cart'] = cart

    messages.success(request, "✅ Added to cart successfully!")
    return redirect('home')


# 🛒 CART VIEW
def cart_view(request):
    cart = request.session.get('cart', {})
    items = []
    grand_total = 0

    for pid, qty in cart.items():
        product = get_object_or_404(Product, id=pid)
        total = product.price * qty
        grand_total += total

        items.append({
            'product': product,
            'qty': qty,
            'total': total
        })

    return render(request, 'inventory/cart.html', {
        'items': items,
        'grand_total': grand_total
    })


def confirm_payment(request):
    cart = request.session.get('cart', {})

    if not cart:
        messages.warning(request, "Your cart is empty.")
        return redirect('home')

    for pid, qty in cart.items():
        product = get_object_or_404(Product, id=pid)

        # Save sale
        Sale.objects.create(
            product=product,
            quantity=qty,
            total_price=product.price * qty
        )

        # Create order history
        Order.objects.create(
            user=None,
            product=product,
            quantity=qty,
            price=product.price * qty,
            status="shipping"
        )

        # Reduce stock
        product.quantity = max(product.quantity - qty, 0)
        product.save()

    request.session['cart'] = {}

    messages.success(request, "🎉 Your order has been placed successfully!")
    return render(request, 'inventory/thankyou.html')



def dashboard(request):
    products = Product.objects.all()
    sales = Sale.objects.all().order_by('-sold_at')

    # ✅ Warehouse-wise stock
    stocks = Stock.objects.select_related('product', 'warehouse')

    # ✅ Global stock per product
    product_summary = []
    for product in products:
        total_stock = Stock.objects.filter(product=product).aggregate(
            total=Sum('quantity')
        )['total'] or 0

        product_summary.append({
            'product': product,
            'total_stock': total_stock
        })

    # ✅ Revenue
    total_revenue = Sale.objects.aggregate(
        total=Sum('total_price')
    )['total'] or 0

    # ✅ Items sold
    total_items_sold = Sale.objects.aggregate(
        total=Sum('quantity')
    )['total'] or 0

    # ✅ LOW STOCK (based on GLOBAL stock — correct logic)
    low_stock_count = sum(
        1 for item in product_summary
        if item['total_stock'] <= item['product'].reorder_level
    )

    context = {
        'products': products,
        'sales': sales,
        'stocks': stocks,
        'product_summary': product_summary,  # ⭐ IMPORTANT
        'total_revenue': total_revenue,
        'total_items_sold': total_items_sold,
        'low_stock_count': low_stock_count,
    }

    return render(request, 'inventory/dashboard.html', context)


# 📦 ORDER HISTORY
def order_history(request):

    orders = Order.objects.all().order_by('-created_at')

    order_list = []

    for order in orders:

        days_passed = (timezone.now() - order.created_at).days

        if days_passed >= 3:
            status = "delivered"
        elif days_passed >= 1:
            status = "shipping"
        else:
            status = "pending"

        estimated_delivery = order.created_at + timedelta(days=3)

        order_list.append({
            "product": order.product,
            "quantity": order.quantity,
            "created_at": order.created_at,
            "status": status,
            "delivery": estimated_delivery
        })

    return render(request, "inventory/order_history.html", {
        "orders": order_list
    })