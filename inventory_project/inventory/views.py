from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum, F
from django.core.paginator import Paginator
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from datetime import timedelta

from .models import Product, Sale, Stock, Warehouse, Order


# 🏠 HOME
def home(request):
    query = request.GET.get('q')

    products = Product.objects.all().order_by('-created_at')

    if query:
        products = products.filter(name__contains=query)

    # Pagination (important for large inventory)
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)

    return render(request, 'inventory/home.html', {
        'products': products
    })


# 🛒 ADD TO CART
def add_to_cart(request, id):

    product = get_object_or_404(Product, id=id)

    cart = request.session.get('cart', {})

    cart[str(id)] = cart.get(str(id), 0) + 1

    request.session['cart'] = cart

    messages.success(request, "Added to cart successfully!")

    return redirect('home')


# 🛒 CART VIEW
def cart_view(request):

    cart = request.session.get('cart', {})

    items = []
    grand_total = 0

    products = Product.objects.filter(id__in=cart.keys())

    for product in products:

        qty = cart.get(str(product.id), 0)

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


# 💳 CONFIRM PAYMENT
def confirm_payment(request):

    cart = request.session.get('cart', {})

    if not cart:
        messages.warning(request, "Your cart is empty.")
        return redirect('home')

    products = Product.objects.filter(id__in=cart.keys())

    for product in products:

        qty = cart.get(str(product.id))

        # ❗ Prevent negative stock
        if product.quantity < qty:
            messages.error(request, f"Not enough stock for {product.name}")
            return redirect('cart')

        # Save sale
        Sale.objects.create(
            product=product,
            quantity=qty,
            total_price=product.price * qty
        )

        # Create order history
        Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            product=product,
            quantity=qty,
            price=product.price * qty,
            status="shipping"
        )

        # Safe stock reduction
        Product.objects.filter(id=product.id).update(
            quantity=F('quantity') - qty
        )

    request.session['cart'] = {}

    messages.success(request, "Your order has been placed successfully!")

    return render(request, 'inventory/thankyou.html')


# 📊 DASHBOARD
@login_required
def dashboard(request):

    products = Product.objects.only('id', 'name', 'quantity', 'price')

    sales = Sale.objects.select_related('product').order_by('-sold_at')

    stocks = Stock.objects.select_related('product', 'warehouse')

    # Global stock summary
    product_summary = Stock.objects.values(
    'product__id',
    'product__name',
    'product__brand',
    'product__reorder_level'
    ).annotate(
    total_stock=Sum('quantity')
    )

    # Revenue
    total_revenue = Sale.objects.aggregate(
        total=Sum('total_price')
    )['total'] or 0

    # Items sold
    total_items_sold = Sale.objects.aggregate(
        total=Sum('quantity')
    )['total'] or 0

    # Low stock count
    low_stock_count = sum(
        1 for item in product_summary
        if item['total_stock'] <= item['product__reorder_level']
    )

    context = {
        'products': products,
        'sales': sales,
        'stocks': stocks,
        'product_summary': product_summary,
        'total_revenue': total_revenue,
        'total_items_sold': total_items_sold,
        'low_stock_count': low_stock_count,
    }

    return render(request, 'inventory/dashboard.html', context)


# 📦 ORDER HISTORY
def order_history(request):

    orders = Order.objects.select_related('product').order_by('-created_at')

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