from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Product


def home(request):
    query = request.GET.get('q')

    if query:
        products = Product.objects.filter(name__icontains=query)
    else:
        products = Product.objects.all()

    return render(request, 'inventory/home.html', {
        'products': products
    })


def add_to_cart(request, id):
    # get cart from session
    cart = request.session.get('cart', {})

    # increase quantity
    cart[str(id)] = cart.get(str(id), 0) + 1

    # save back to session
    request.session['cart'] = cart

    # ⭐ SUCCESS MESSAGE
    messages.success(request, "✅ Added to cart successfully!")

    return redirect('home')


def cart_view(request):
    cart = request.session.get('cart', {})
    items = []
    grand_total = 0

    for pid, qty in cart.items():
        product = get_object_or_404(Product, id=pid)  # safer
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
    # clear cart after payment
    request.session['cart'] = {}

    messages.success(request, "🎉 Thank you for visiting Lachu Auto Traders!")

    return render(request, 'inventory/thankyou.html')