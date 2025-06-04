from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile', null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    address = models.TextField()

    def __str__(self):
        return self.name
    
class Drink(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='drinks/', blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.price} kr"
    
class OrderDrink(models.Model):
    order = models.ForeignKey('Order', related_name='order_drinks', on_delete=models.CASCADE)
    drink = models.ForeignKey(Drink, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_at_time = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}x {self.drink.name}"

class Pizza(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='pizzas/')

    def __str__(self):
        return self.name


class PizzaSize(models.Model):
    SIZE_CHOICES = [
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
    ]
    pizza = models.ForeignKey(Pizza, related_name="sizes", on_delete=models.CASCADE)
    size = models.CharField(max_length=1, choices=SIZE_CHOICES)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.pizza.name} ({self.get_size_display()})"


class Topping(models.Model):
    name = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.name


class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('ON_THE_WAY', 'On the Way'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    def __str__(self):
        return f"Order #{self.id} - {self.customer.name} - {self.get_status_display()}"
   
    def calculate_total(self):
        pizzas_total = sum(item.price_at_time * item.quantity for item in self.order_pizzas.all())
        drinks_total = sum(drink.price_at_time * drink.quantity for drink in self.order_drinks.all())
        self.total = pizzas_total + drinks_total
        self.save()


class OrderPizza(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_pizzas')
    pizza = models.ForeignKey(Pizza, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    size = models.ForeignKey(PizzaSize, on_delete=models.CASCADE, null=True, blank=True)
    price_at_time = models.DecimalField(max_digits=6, decimal_places=2)
    special_instructions = models.TextField(blank=True)
    toppings = models.ManyToManyField(Topping, through='OrderPizzaTopping', related_name='order_pizzas')

    def __str__(self):
        size_display = self.size.get_size_display() if self.size else 'No Size'
        return f"{self.quantity}x {self.pizza.name} ({size_display}) (Order #{self.order.id})"


class OrderPizzaTopping(models.Model):
    order_pizza = models.ForeignKey(OrderPizza, on_delete=models.CASCADE)
    topping = models.ForeignKey(Topping, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.topping.name} on {self.order_pizza}"
