from django.db import models

from django.contrib.auth.models import User


# Create your models here.
class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    address = models.TextField()

    def __str__(self):
        return self.name
    
class Pizza(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to="pizzas/")

    def __str__(self):
        return self.name

class Order(models.Model):
    Customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    pizzas = models.ManyToManyField(Pizza) 
    total = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DataTimeField (auto_now_add=True)
    

    def __str__(self):
            return f"Order by {self.customer.name} - ${self.total}"

