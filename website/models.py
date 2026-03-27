from django.db import models
from django.contrib.auth.models import User


class Product(models.Model):
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=100)
    brand = models.CharField(max_length=100)
    price = models.FloatField()
    condition = models.CharField(max_length=50)
    sustainability_score = models.IntegerField()
    ethical_score = models.IntegerField()
    image_url = models.URLField(blank=True, null=True)
    image_file = models.ImageField(upload_to='product_images/', blank=True, null=True)

    def __str__(self):
        return self.name

    @property
    def image(self):
        """Returns whichever image exists — file or URL"""
        if self.image_file:
            return self.image_file.url
        elif self.image_url:
            return self.image_url
        return '/static/default.jpg'


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"