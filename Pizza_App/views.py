from django.shortcuts import render

from .models import Pizza, Order, Customer

def home(request):
    return render(request, 'Pizza_App/home.html')

def menu(request):
    pizzas = Pizza.objects.all()
    return render(request, 'menu.html', {'pizzas': pizzas})

def place_order(request):
    pizzas = Pizza.objects.all()

    if request.method == "POST":
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        address = request.POST['address']
        selected_pizzas = request.POST.getlist('pizzas')

        # Find or create the customer
        customer, created = Customer.objects.get_or_create(
            email=email,
            defaults={'name': name, 'phone': phone, 'address': address}
        )

        # Calculate the order total
        total = sum(Pizza.objects.filter(id__in=selected_pizzas).values_list('price', flat=True))

        # Create the order linked to the customer
        new_order = Order.objects.create(customer=customer, total=total)
        new_order.pizzas.add(*selected_pizzas)

        return render(request, 'confirmation.html', {'order': new_order})

    return render(request, 'order.html', {'pizzas': pizzas})
