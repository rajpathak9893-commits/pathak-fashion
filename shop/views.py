from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Sum
from .models import Profile
from .forms import ProfileForm


# FIX: Sabhi models ek jagah import karo — pehle Wishlist missing thi
from .models import Product, Cart, Order, Wishlist
from .forms import ProfileUpdateForm


# ===============================
# 🔧 HELPER FUNCTION
# FIX: Wishlist fetch code 3 views mein repeat tha — ab ek jagah hai
# ===============================
def get_wishlist_ids(user):
    if user.is_authenticated:
        return Wishlist.objects.filter(user=user).values_list('product_id', flat=True)
    return []


# ===============================
# 🏠 SHOP
# ===============================
def record(request):
    data = Product.objects.all()
    return render(request, 'shop.html', {
        'database_records': data,
        'wishlist_ids': get_wishlist_ids(request.user)
    })


# ===============================
# 👨 MEN
# ===============================
def men(request):
    data = Product.objects.filter(category='men')
    return render(request, 'men.html', {
        'database_records': data,
        'wishlist_ids': get_wishlist_ids(request.user)
    })


# ===============================
# 👩 WOMEN
# ===============================
def women(request):
    sub = request.GET.get('sub')
    if sub:
        data = Product.objects.filter(category='women', subcategory=sub)
    else:
        data = Product.objects.filter(category='women')

    return render(request, 'women.html', {
        'database_records': data,
        'wishlist_ids': get_wishlist_ids(request.user)
    })


# ===============================
# 📄 PRODUCT DETAIL
# ===============================
def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    return render(request, 'product_detail.html', {'product': product})


# ===============================
# 🛒 ADD TO CART
# ===============================
@login_required(login_url='login')
def add_to_cart(request, id):
    product = get_object_or_404(Product, id=id)

    if product.stock <= 0:
        messages.error(request, "Out of stock!")
        return redirect('shop')

    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        product=product
    )

    if not created:
        if cart_item.quantity < product.stock:
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, "Item added to cart!")  # FIX: sirf tab message jab quantity badhti hai
        else:
            messages.warning(request, "Stock limit reached!")
    else:
        messages.success(request, "Item added to cart!")

    return redirect('cart')


# ===============================
# 🛒 CART
# FIX: select_related lagaya — N+1 query problem khatam
# FIX: sum DB level pe — Python loop nahi
# ===============================
@login_required(login_url='login')
def cart(request):
    items = Cart.objects.filter(user=request.user).select_related('product')
    total = items.aggregate(
        total=Sum('product__price')
    )['total'] or 0

    # Note: quantity ke saath total ke liye Python loop theek hai kyunki
    # Cart.total_price property use ho rahi hai
    total = sum(item.total_price for item in items)

    return render(request, 'cart.html', {
        'items': items,
        'total': total
    })


# ===============================
# ❌ REMOVE FROM CART
# ===============================
@login_required(login_url='login')
def remove_from_cart(request, id):
    item = get_object_or_404(Cart, id=id, user=request.user)
    item.delete()
    messages.warning(request, "Item removed from cart!")
    return redirect('cart')


# ===============================
# ➕ INCREASE QUANTITY
# ===============================
@login_required(login_url='login')
def increase_quantity(request, id):
    item = get_object_or_404(Cart, id=id, user=request.user)

    if item.quantity < item.product.stock:
        item.quantity += 1
        item.save()
    else:
        messages.warning(request, "Stock limit reached!")

    return redirect('cart')


# ===============================
# ➖ DECREASE QUANTITY
# ===============================
@login_required(login_url='login')
def decrease_quantity(request, id):
    item = get_object_or_404(Cart, id=id, user=request.user)

    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    else:
        item.delete()

    return redirect('cart')


# ===============================
# ⚡ BUY NOW
# FIX: POST check lagaya — GET se order nahi hona chahiye
# ===============================
@login_required(login_url='login')
def buy_now(request, id):
    if request.method != 'POST':
        return redirect('shop')

    product = get_object_or_404(Product, id=id)

    if product.stock <= 0:
        messages.error(request, "Out of stock!")
        return redirect('shop')

    with transaction.atomic():
        # FIX: select_for_update — race condition fix
        product = Product.objects.select_for_update().get(id=id)

        if product.stock <= 0:
            messages.error(request, "Out of stock!")
            return redirect('shop')

        order = Order.objects.create(
            user=request.user,
            product=product,
            quantity=1,
            total_price=product.price
        )

        product.stock -= 1
        product.save()

    request.session['latest_order_id'] = order.id
    return redirect('success')


# ===============================
# 📦 ORDERS
# ===============================
@login_required(login_url='login')
def orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-id')
    latest_order_id = request.session.get('latest_order_id')

    return render(request, 'orders.html', {
        'orders': orders,
        'latest_order_id': latest_order_id
    })


# ===============================
# 🧾 CHECKOUT
# ===============================
@login_required(login_url='login')
def checkout(request):
    items = Cart.objects.filter(user=request.user).select_related('product')
    total = sum(item.total_price for item in items)

    return render(request, 'checkout.html', {
        'items': items,
        'total': total
    })


# ===============================
# ✅ PLACE ORDER
# FIX: transaction.atomic + select_for_update — race condition / overselling fix
# FIX: product_name typo fix (Product_name → product_name)
# FIX: POST check lagaya
# ===============================
@login_required(login_url='login')
def place_order(request):
    if request.method != 'POST':
        return redirect('cart')

    items = Cart.objects.filter(user=request.user).select_related('product')

    if not items.exists():
        return redirect('cart')

    with transaction.atomic():
        for item in items:
            # FIX: select_for_update — concurrent requests mein overselling nahi hogi
            product = Product.objects.select_for_update().get(id=item.product.id)

            if item.quantity > product.stock:
                # FIX: product_name lowercase — pehle crash ho raha tha
                messages.error(request, f"{product.product_name} ka stock kam hai!")
                return redirect('cart')

            Order.objects.create(
                user=request.user,
                product=product,
                quantity=item.quantity,
                total_price=product.price * item.quantity
            )

            product.stock -= item.quantity
            product.save()

        items.delete()

    messages.success(request, "Order placed successfully!")
    return redirect('orders')


# ===============================
# 📞 CONTACT
# ===============================
def contact(request):
    return render(request, 'contact.html')


# ===============================
# 🎉 SUCCESS
# FIX: Session clear kiya — refresh pe order dobara nahi dikhega
# ===============================
# from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def success(request):
    order_id = request.session.get('latest_order_id')
    order = None

    if order_id:
        order = Order.objects.filter(
            id=order_id,
            user=request.user
        ).first()

        # SAFE remove (error nahi aayega)
        request.session.pop('latest_order_id', None)

    return render(request, 'success.html', {'order': order})

# ===============================
# 👤 EDIT PROFILE
# ===============================
@login_required
# from django.shortcuts import render, redirect
# from .models import Profile
# from .forms import ProfileForm

def edit_profile(request):
    # ✅ YAHI MAIN FIX HAI
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')   # ya jo bhi tumhara page hai
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'edit_profile.html', {
        'form': form,
        'profile': profile   # 👈 important
    })
# ===============================
# 📊 DASHBOARD
# FIX: DB-level aggregation — Python loop nahi
# ===============================
@login_required
def dashboard(request):
    orders = Order.objects.filter(user=request.user)
    total_orders = orders.count()
    # FIX: Sum() DB pe calculate hota hai — fast & accurate
    total_spent = orders.aggregate(total=Sum('total_price'))['total'] or 0

    return render(request, 'dashboard.html', {
        'orders': orders,
        'total_orders': total_orders,
        'total_spent': total_spent
    })


# ===============================
# 🧾 ORDER DETAIL
# ===============================
@login_required
def order_detail(request, id):
    order = get_object_or_404(Order, id=id, user=request.user)
    return render(request, 'order_detail.html', {'order': order})


# ===============================
# ❤️ TOGGLE WISHLIST (toggle_wishlist + wishlist dono same kaam karte hain)
# FIX: Wishlist import fix, duplicate commented code hata diya
# ===============================
@login_required(login_url='login')
def wishlist(request, id):
    product = get_object_or_404(Product, id=id)
    item, created = Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )
    if not created:
        item.delete()
        messages.warning(request, "Removed from wishlist!")
    else:
        messages.success(request, "Added to wishlist ❤️")
    return redirect(request.META.get('HTTP_REFERER', 'shop'))


@login_required(login_url='login')
def toggle_wishlist(request, id):
    product = get_object_or_404(Product, id=id)

    item, created = Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )

    if not created:
        item.delete()
        messages.warning(request, "Removed from wishlist!")
    else:
        messages.success(request, "Added to wishlist ❤️")

    return redirect(request.META.get('HTTP_REFERER', 'shop'))


# ===============================
# ❤️ WISHLIST PAGE
# ===============================
@login_required(login_url='login')
def wishlist_page(request):
    items = Wishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'wishlist.html', {'items': items})


# ===============================
# ❌ REMOVE FROM WISHLIST
# ===============================
@login_required(login_url='login')
def remove_wishlist(request, id):
    item = get_object_or_404(Wishlist, id=id, user=request.user)
    item.delete()
    return redirect('wishlist_page')
import razorpay
from django.conf import settings

def payment(request):
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    amount = 500 * 100  # ₹500 = 50000 paise

    payment_order = client.order.create({
        'amount': amount,
        'currency': 'INR',
        'payment_capture': '1'
    })

    context = {
        'order_id': payment_order['id'],
        'amount': amount,
        'razorpay_key': settings.RAZORPAY_KEY_ID
    }

    return render(request, 'payment.html', context)
from django.db.models import Q

def search(request):
    query = request.GET.get('q')
    results = []

    if query:
        results = Product.objects.filter(
            Q(product_name__icontains=query) |
            Q(category__icontains=query) |
            Q(subcategory__icontains=query)
        )

    return render(request, 'search.html', {
    'results': results,
    'query': query,
    'wishlist_ids': get_wishlist_ids(request.user)  # 👈 ADD THIS
})