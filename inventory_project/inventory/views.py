from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum, F
from django.db.models.functions import TruncDay, TruncMonth
from django.core.paginator import Paginator
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from datetime import timedelta
from decimal import Decimal
import json

# 🔥 Tally Integration
from .tally_integration import (
    create_sales_entry,
    create_stock_item,
    create_customer
)

from .models import Product, Sale, Order


# 🏠 HOME
def home(request):
    query = request.GET.get('q')

    products = Product.objects.all().order_by('-created_at')

    if query:
        products = products.filter(name__icontains=query)

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
    grand_total = Decimal('0')

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

    customer_name = (
        request.user.username
        if request.user.is_authenticated
        else "Walk-in Customer"
    )

    # ✅ Safe customer creation
    try:
        create_customer(customer_name)
    except Exception as e:
        print("Customer Error:", e)

    for product in products:
        qty = cart.get(str(product.id))

        if product.quantity < qty:
            messages.error(request, f"Not enough stock for {product.name}")
            return redirect('cart')

        # ✅ SAFE TALLY CALLS
        try:
            create_stock_item(product.name, product.quantity)

            create_sales_entry(
                product.name,
                qty,
                product.price,
                customer_name
            )

        except Exception as e:
            print("Tally Error:", e)

        # ✅ Save sale (this must ALWAYS run)
        Sale.objects.create(
            product=product,
            quantity=qty,
            total_price=product.price * qty
        )

        # ✅ Save order
        Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            product=product,
            quantity=qty,
            price=product.price * qty,
            status="shipping"
        )

        # ✅ Reduce stock safely
        Product.objects.filter(id=product.id).update(
            quantity=F('quantity') - qty
        )

    request.session['cart'] = {}

    messages.success(request, "Your order has been placed successfully!")
    return render(request, 'inventory/thankyou.html')


# 📊 DASHBOARD
@login_required
def dashboard(request):

    filter_type = request.GET.get('filter')
    sales = Sale.objects.all()

    if filter_type == '7days':
        sales = sales.filter(sold_at__gte=timezone.now() - timedelta(days=7))
    elif filter_type == '30days':
        sales = sales.filter(sold_at__gte=timezone.now() - timedelta(days=30))

    products = Product.objects.all()

    total_revenue = sales.aggregate(total=Sum('total_price'))['total'] or Decimal('0')
    total_items_sold = sales.aggregate(total=Sum('quantity'))['total'] or 0

    low_stock_products = Product.objects.filter(quantity__lte=F('reorder_level'))

    top_products = (
        sales.values('product__name')
        .annotate(total_sold=Sum('quantity'))
        .order_by('-total_sold')[:5]
    )

    daily_sales_qs = (
        sales.annotate(day=TruncDay('sold_at'))
        .values('day')
        .annotate(total=Sum('total_price'))
        .order_by('day')
    )

    daily_sales = [
        {"day": str(d["day"].date()), "total": float(d["total"])}
        for d in daily_sales_qs if d["total"]
    ]

    monthly_sales_qs = (
        sales.annotate(month=TruncMonth('sold_at'))
        .values('month')
        .annotate(total=Sum('total_price'))
        .order_by('month')
    )

    monthly_sales = [
        {"month": str(m["month"].date()), "total": float(m["total"])}
        for m in monthly_sales_qs if m["total"]
    ]

    total_cost = total_revenue * Decimal('0.7')
    total_profit = total_revenue - total_cost

    context = {
        'products': products,
        'sales': sales,
        'total_revenue': total_revenue,
        'total_items_sold': total_items_sold,
        'low_stock_products': low_stock_products,
        'top_products': top_products,
        'daily_sales': json.dumps(daily_sales),
        'monthly_sales': json.dumps(monthly_sales),
        'total_profit': total_profit,
    }

    return render(request, 'inventory/dashboard.html', context)


# 🔄 REFUND
def refund_order(request, id):

    order = get_object_or_404(Order, id=id)

    if getattr(order, 'is_refunded', False):
        messages.warning(request, "Already refunded!")
        return redirect('order_history')

    if order.status in ['pending', 'shipping']:
        order.status = 'cancelled'
    elif order.status == 'delivered':
        order.status = 'returned'

    order.is_refunded = True
    order.save()

    Product.objects.filter(id=order.product.id).update(
        quantity=F('quantity') + order.quantity
    )

    messages.success(request, "Refund processed successfully!")
    return redirect('order_history')


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
            "id": order.id,
            "product": order.product,
            "quantity": order.quantity,
            "created_at": order.created_at,
            "status": status,
            "delivery": estimated_delivery,
            "is_refunded": getattr(order, 'is_refunded', False)
        })

    return render(request, "inventory/order_history.html", {
        "orders": order_list
    })