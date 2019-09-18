from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from django.contrib.auth.models import User

# class User(AbstractBaseUser):
#     """
#     Email and phone are not required because user can login by email or phone.
#     We need check unique of this fields in serializers
#     """
#     email = models.EmailField(blank=True, null=True)

#     USERNAME_FIELD = 'email'

class Dish(models.Model):
    name = models.TextField(max_length=100)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    unit = models.CharField(max_length=10)
    category = models.CharField(max_length=50)
    restaurant = models.IntegerField(blank=True,null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Dish"
        verbose_name_plural = "Dishes"

class Cart(models.Model):
    user = models.OneToOneField(User)
    total_price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    restaurant = models.CharField(max_length=500)

    class Meta:
        verbose_name = "Cart"
        verbose_name_plural = "Cart"


class CartItems(models.Model):
    user = models.ForeignKey(User, related_name='cart_item')
    items = models.ForeignKey(Dish, blank=True)
    cart = models.ForeignKey(Cart, blank=True,null=True,related_name='cart_item')
    quantity = models.IntegerField(blank=True,null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)

    class Meta:
        verbose_name = "CartItem"
        verbose_name_plural = "CartItems"

class Order(models.Model):
    user = models.ForeignKey(User, related_name='order')
    order_date = models.DateField()
    total_price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    restaurant = models.CharField(max_length=500)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Oredrs"

class OrderItems(models.Model):
    user = models.ForeignKey(User, related_name='order_item')
    items = models.ForeignKey(Dish, blank=True)
    order = models.ForeignKey(Order, blank=True,null=True,related_name='order_item')
    quantity = models.IntegerField(blank=True,null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)

    class Meta:
        verbose_name = "CartItem"
        verbose_name_plural = "CartItems"



