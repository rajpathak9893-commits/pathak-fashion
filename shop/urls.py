from django.urls import path
from . import views

urlpatterns = [

    path('', views.record, name="shop"),

    path('men/', views.men, name="men"),
    path('women/', views.women, name="women"),

    path('contact/', views.contact, name="contact"),

    path('product/<int:id>/', views.product_detail, name="product_detail"),

    path('add-to-cart/<int:id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart, name='cart'),

    path('remove/<int:id>/', views.remove_from_cart, name='remove'),
    path('increase/<int:id>/', views.increase_quantity, name='increase'),
    path('decrease/<int:id>/', views.decrease_quantity, name='decrease'),

    # 🔥 NEW
    path('buy/<int:id>/', views.buy_now, name='buy_now'),
    path('orders/', views.orders, name='orders'),
    path('checkout/', views.checkout, name='checkout'),
    path('place-order/', views.place_order, name='place_order'),
    path('success/', views.success, name='success'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('order/<int:id>/', views.order_detail, name='order_detail'),
    # path('wishlist/<int:id>/', views.toggle_wishlist, name='wishlist'),
    path('wishlist/', views.wishlist_page, name='wishlist_page'),
    path('wishlist/<int:id>/', views.wishlist, name='wishlist'),
    path('remove-wishlist/<int:id>/', views.remove_wishlist, name='remove_wishlist'),
    path('payment/', views.payment, name='payment'),
    path('search/', views.search, name='search'),

]