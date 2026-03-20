from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum, F
from django.db.models.functions import TruncDay, TruncMonth
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import json

# 🔥 Tally Integration (FIXED IMPORTS)
from .tally_integration import (
    create_sales_entry,
    create_stock_item,
    create_customer,
    get_stock_summary,
    parse_stock_summary
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

    # ❌ REMOVED: Do not recreate Master on every checkout, it wipes their Opening Balance!
    # try:
    #     create_customer(customer_name)
    # except Exception as e:
    #     print("Customer Error:", e)

    for product in products:
        qty = cart.get(str(product.id))

        if product.quantity < qty:
            messages.error(request, f"Not enough stock for {product.name}")
            return redirect('cart')

        try:
            # ❌ REMOVED: Do not recreate Stock Item! It resets Opening Balance to 0!
            # create_stock_item(product.name)

            create_sales_entry(
                product.name,
                qty,
                float(product.price),
                customer_name
            )

        except Exception as e:
            print("Tally Error:", e)

        # ✅ Save sale
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

        # ✅ Reduce stock
        Product.objects.filter(id=product.id).update(
            quantity=F('quantity') - qty
        )

    request.session['cart'] = {}

    messages.success(request, "Your order has been placed successfully!")
    return render(request, 'inventory/thankyou.html')


# 📊 DASHBOARD
def dashboard(request):

    sales = Sale.objects.all()
    products = Product.objects.all()

    total_revenue = sales.aggregate(total=Sum('total_price'))['total'] or Decimal('0')
    total_items_sold = sales.aggregate(total=Sum('quantity'))['total'] or 0

    # 📊 Charts
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

    # 🔥 TALLY STOCK FETCH
    try:
        stock_xml = get_stock_summary()
        stock_data = parse_stock_summary(stock_xml) if stock_xml else []
    except Exception as e:
        print("Tally Fetch Error:", e)
        stock_data = []

    context = {
        'products': products,
        'sales': sales,
        'total_revenue': total_revenue,
        'total_items_sold': total_items_sold,
        'daily_sales': json.dumps(daily_sales),

        # 🔥 Tally Data
        'tally_stock': stock_data,
    }

    return render(request, 'inventory/dashboard.html', context)


# 🔄 REFUND
def refund_order(request, id):
    order = get_object_or_404(Order, id=id)

    order.status = 'cancelled'
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

    return render(request, "inventory/order_history.html", {
        "orders": orders
    })