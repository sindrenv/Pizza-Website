from django.shortcuts import redirect, render

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