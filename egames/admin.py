from django.contrib import admin
from egames.models import Game, Customer, Role, Staff, Order, OrderItem, CustomerGame

admin.site.register(Game)
admin.site.register(Customer)
admin.site.register(Role)
admin.site.register(Staff)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(CustomerGame)
