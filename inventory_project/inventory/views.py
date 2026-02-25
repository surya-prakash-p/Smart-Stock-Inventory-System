from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum, F
from .models import Product, Sale, Stock, Warehouse


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


# 💳 CONFIRM PAYMENT (STOCK ↓ + SALE SAVE)
def confirm_payment(request):
    cart = request.session.get('cart', {})

    if not cart:
        messages.warning(request, "Your cart is empty.")
        return redirect('home')

    for pid, qty in cart.items():
        product = get_object_or_404(Product, id=pid)

        # ✅ Save sale
        Sale.objects.create(
            product=product,
            quantity=qty,
            total_price=product.price * qty
        )

        # ✅ Reduce stock
        product.quantity = max(product.quantity - qty, 0)
        product.save()

    # ✅ Clear cart
    request.session['cart'] = {}

    messages.success(request, "🎉 Your order has been placed successfully!")
    return render(request, 'inventory/thankyou.html')


from django.db.models import Sum, F
from .models import Product, Sale, Stock, Warehouse


def dashboard(request):
    products = Product.objects.all()
    sales = Sale.objects.all().order_by('-sold_at')
    stocks = Stock.objects.select_related('product', 'warehouse')

    total_revenue = Sale.objects.aggregate(
        total=Sum('total_price')
    )['total'] or 0

    total_items_sold = Sale.objects.aggregate(
        total=Sum('quantity')
    )['total'] or 0

    low_stock_count = Product.objects.filter(
        stock__quantity__lte=F('reorder_level')
    ).distinct().count()

    context = {
        'products': products,
        'sales': sales,
        'stocks': stocks,  # ⭐ NEW
        'total_revenue': total_revenue,
        'total_items_sold': total_items_sold,
        'low_stock_count': low_stock_count,
    }

    return render(request, 'inventory/dashboard.html', context)