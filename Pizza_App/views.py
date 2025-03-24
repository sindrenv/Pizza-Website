from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User


from .models import Pizza, Order, Customer, OrderPizza

def home(request):
    return render(request, 'Pizza_App/home.html')

def menu(request):
    pizzas = Pizza.objects.all()
    return render(request, 'menu.html', {'pizzas': pizzas})


def order_pizza(request):
    pizzas = Pizza.objects.all()

    if request.method == "POST":
        customer_name = request.POST['name']
        customer_email = request.POST['email']
        customer_phone = request.POST['phone']
        customer_address = request.POST['address']
        pizzas_ids = request.POST.getlist('pizzas')
        quantities = request.POST.getlist('quantities')

        # Find or create the customer
        customer, created = Customer.objects.get_or_create(
            email=customer_email,
            defaults={'name': customer_name, 'phone': customer_phone, 'address': customer_address}
        )

             # Crear el pedido
        order = Order.objects.create(customer=customer, total=0)

        total = 0
        for pizza_id, quantity in zip(pizza_id, quantities):
            pizza = Pizza.objects.get(id=pizza_id)
            quantity = int(quantity)
            OrderPizza.objects.create(order=order, pizza=pizza, quantity=quantity)
            total += pizza.price * quantity

        order.total = total
        order.save()

        return render(request, 'confirmation.html', {
            'customer': customer,
            'order_items': OrderPizza,
            'total': total
        })

    return render(request, 'order.html', {'pizzas': pizzas})

def confirmation(request):
    return render(request, 'confirmation.html')


def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        # Check if passwords match
        if password1 != password2:
            return render(request, "register.html", {"error": "Passwords do not match"})

        # Create the user
        user = User.objects.create_user(username=username, email=email, password=password1)
        login(request, user)  # Log the user in immediately after registration
        return redirect('home')  # Redirect to the home page after successful registration

    return render(request, "register.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect(request.GET.get("next", "home"))  # Redirects to home after login
        else:
            return render(request, "login.html", {
                "username": username,
                "error": "Wrong password"
            })
    
    return render(request, "login.html")
