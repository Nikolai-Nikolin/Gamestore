from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.db.models import CASCADE
from django.utils import timezone


class Game(models.Model):
    def __str__(self):
        return self.title

    title = models.CharField(max_length=30)
    cover_image = models.ImageField(default=None, blank=True)
    price = models.FloatField(null=False)
    discount_percent = models.FloatField(default=0)
    final_price = models.FloatField(default=0)
    description = models.TextField(max_length=200)
    is_deleted = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.final_price = self.price - (self.price * self.discount_percent // 100)
        super(Game, self).save(*args, **kwargs)


class Genre(models.Model):
    def __str__(self):
        return self.title_genre

    title_genre = models.CharField(max_length=50)
    description = models.TextField(max_length=200)
    game = models.ManyToManyField(Game)
    is_deleted = models.BooleanField(default=False)


class Gamer(User):
    def __str__(self):
        return self.username

    birth_date = models.DateField(blank=False, default=None, null=True)
    wallet = models.FloatField(default=0)
    is_deleted = models.BooleanField(default=False)


class Purchase(models.Model):
    def __str__(self):
        return f'{self.game.title} - {self.timestamp}'

    gamer = models.ForeignKey(Gamer, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)


class Library(models.Model):
    gamer = models.ForeignKey(Gamer, on_delete=models.CASCADE, default=timezone.now)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    added_date = models.DateTimeField(auto_now_add=True)


class Review(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    gamer = models.ForeignKey(Gamer, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)


class Friend(models.Model):
    gamer = models.ForeignKey(Gamer, related_name='friends', on_delete=models.CASCADE)
    friend = models.ForeignKey(Gamer, on_delete=models.CASCADE)


class Wishlist(models.Model):
    gamer = models.ForeignKey(Gamer, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)


class Role(models.Model):
    def __str__(self):
        return self.role_name

    role_name = models.CharField(max_length=20, null=False, unique=True)
    is_deleted = models.BooleanField(default=False)


class Staff(User):
    def __str__(self):
        return self.username

    role = models.ForeignKey(Role, on_delete=CASCADE, null=True)
    is_deleted = models.BooleanField(default=False)
