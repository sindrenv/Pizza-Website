from django.db import models

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
        image = models.ImageField(upload_to='pizzas/')

        def __str__(self):
            return self.name

class Order(models.Model):
        customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
        total = models.DecimalField(max_digits=8, decimal_places=2)
        created_at = models.DateTimeField(auto_now_add=True)

        def __str__(self):
            return f"Order by {self.customer.name} - ${self.total}"
        
        def calculate_total(self):
            total = sum(item.pizza.price * item.quantity for item in self.order_pizzas.all())
            self.total = total
            self.save()
        
class OrderPizza(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    pizza = models.ForeignKey(Pizza, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_at_time = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}x {self.pizza.name} (Order #{self.order.id})"


