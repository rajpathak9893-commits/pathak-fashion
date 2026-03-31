from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


# ===============================
# 🛍️ PRODUCT MODEL
# ===============================
class Product(models.Model):
    product_name = models.CharField(max_length=30)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=300)
    pub_date = models.DateField()
    image = models.ImageField(upload_to="products/")
    stock = models.IntegerField(default=10)

    CATEGORY_CHOICES = (
    ('men', 'Men'),
    ('women', 'Women'),
    ('kids', 'Kids'),
)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='men')

    SUBCATEGORY_CHOICES = (
        ('lehenga', 'Lehenga'),
        ('kurti', 'Kurti'),
        ('saree', 'Saree'),
        ('gown', 'Gown'),
        ('kurta', 'Kurta'),
        ('sherwani', 'Sherwani'),
        ('shirt', 'Shirt'),
        ('trouser', 'Trouser'),
    )
    subcategory = models.CharField(max_length=20, choices=SUBCATEGORY_CHOICES, default='kurti')

    is_new = models.BooleanField(default=False)
    is_best = models.BooleanField(default=False)

    # FIX: 0-100 ke beech hi hoga
    discount = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    def __str__(self):
        return self.product_name


# ===============================
# 📦 PRODUCT IMAGE GALLERY
# ===============================
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_gallery/')

    def __str__(self):
        return self.product.product_name


# ===============================
# 🛒 CART MODEL
# ===============================
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    class Meta:
        unique_together = ('user', 'product')

    @property
    def total_price(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.user.username} - {self.product.product_name}"


# ===============================
# 📦 ORDER MODEL
# ===============================
class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.total_price:
            self.total_price = self.product.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.product.product_name}"


# ===============================
# 👤 USER PROFILE MODEL
# ===============================
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='profile/', default='default.png')

    def __str__(self):
        return self.user.username


# ===============================
# ❤️ WISHLIST MODEL
# ===============================
class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username} - {self.product.product_name}"


# ===============================
# ⭐ PRODUCT REVIEW MODEL
# ===============================
class ProductReview(models.Model):
    RATING_CHOICES = [(i, i) for i in range(1, 6)]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    comment = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'user')

    def __str__(self):
        return f"{self.user.username} - {self.product.product_name} ({self.rating}⭐)"
from django.db.models.signals import post_save
from django.dispatch import receiver
# from django.contrib.auth.models import User

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()