from django.contrib import admin
from .models import Category,Order,OrderPizza,Customer,Pizza, PizzaSize

admin.site.register(Order)
admin.site.register(Category)
admin.site.register(OrderPizza)
admin.site.register(Customer)
admin.site.register(Pizza)
admin.site.register(PizzaSize)
