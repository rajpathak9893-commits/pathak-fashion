from django.contrib import admin
from django.utils.html import format_html
from .models import Product, ProductImage, Cart, Order, Profile

# 🔥 PRODUCT ADMIN (PRO)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'category', 'subcategory', 'stock', 'image_tag')
    list_filter = ('category', 'subcategory')
    search_fields = ('product_name',)
    list_editable = ('price', 'stock')

    # 🔥 IMAGE PREVIEW
    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return "No Image"

    image_tag.short_description = 'Image'


# 🛒 CART ADMIN
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity')


# 📦 ORDER ADMIN
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'total_price', 'status', 'created_at')
    list_filter = ('status',)
    list_editable = ('status',)  # 🔥 direct status change


# 👤 PROFILE ADMIN
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'image')


# REGISTER
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductImage)
admin.site.register(Cart, CartAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Profile, ProfileAdmin)
from .models import ProductReview

class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'comment', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('product__product_name', 'user__username', 'comment')

admin.site.register(ProductReview, ProductReviewAdmin)
product = Product.objects.get(id=1)
all_reviews = product.reviews.all()