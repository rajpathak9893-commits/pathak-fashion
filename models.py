from django.db import models
class Product(models.Model):
    Product_id=models.AutoField
    Product_name=models.CharField(max_length=30)
    price=models.DecimalField(max_digits=10,decimal_places=2)
    desc=models.CharField(max_length=300)
    pub_date=models.DateField()
    image=models.ImageField(upload_to='Product/')