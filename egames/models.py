from django.db import models
from django.contrib.auth.models import User
from django.db.models import CASCADE
from django.db.models.functions import datetime


class Game(models.Model):
    def __str__(self):
        return self.title

    title = models.CharField(max_length=30)
    cover_image = models.ImageField(default=None, blank=True)
    price = models.FloatField(null=False)
    discount_percent = models.FloatField(default=0)
    discount_price = models.FloatField(default=0)
    end_of_discount = models.DateField(default=datetime.datetime.today)
    genre = models.TextField(max_length=50)
    description = models.TextField(max_length=70)
    amount = models.IntegerField()
    is_deleted = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.discount_price = self.price - (self.price * self.discount_percent // 100)
        super(Game, self).save(*args, **kwargs)


class Customer(User):
    def __str__(self):
        return self.customer_first_name

    customer_first_name = models.CharField(max_length=50, blank=True)
    customer_last_name = models.CharField(max_length=150, blank=True)
    customer_email = models.EmailField(blank=True)
    birth_date = models.DateField(blank=True)


class Role(models.Model):
    def __str__(self):
        return self.role_name

    role_name = models.CharField(max_length=20, null=False, unique=True)


class Staff(User):
    def __str__(self):
        return self.staff_username

    staff_username = models.CharField(max_length=50, null=False, unique=True)
    role = models.ForeignKey(Role, on_delete=CASCADE)
    is_deleted = models.BooleanField(default=False)


class Order(models.Model):
    def __str__(self):
        return str(self.id)

    customer = models.ForeignKey(Customer, on_delete=CASCADE)
    order_date = models.DateField(auto_now_add=True)
    status = models.TextField(max_length=50, blank=True)


class OrderItem(models.Model):
    def __str__(self):
        return str(self.id)

    order = models.ForeignKey(Order, on_delete=CASCADE)
    game = models.ForeignKey(Game, on_delete=CASCADE)
    quantity = models.IntegerField(null=False)


class CustomerGame(models.Model):
    customer = models.ForeignKey(Customer, on_delete=CASCADE)
    game = models.ForeignKey(Game, on_delete=CASCADE)
