from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import Pizza, Order, Customer, OrderPizza, PizzaSize
from Pizza_App.models import Customer, Order





def home(request):
    # Just render the home page and use `user.is_authenticated` in the template
    return render(request, 'Pizza_App/home.html')

def menu(request):
    pizzas = Pizza.objects.all()
    return render(request, 'menu.html', {'pizzas': pizzas})

def order(request):
    pizzas = Pizza.objects.all()

    if request.method == "POST":
        customer_name = request.POST['name']
        customer_email = request.POST['email']
        customer_phone = request.POST['phone']
        customer_address = request.POST['address']

        # Create or find customer
        customer, created = Customer.objects.get_or_create(
            email=customer_email,
            defaults={
                'name': customer_name,
                'phone': customer_phone,
                'address': customer_address
            }
        )

        # Create new order
        order = Order.objects.create(customer=customer, total=0)
        total = 0

        # Loop through pizzas and add to order
        for pizza in pizzas:
            quantity_str = request.POST.get(f'quantity_{pizza.id}')
            size_id = request.POST.get(f'pizza_size_id_{pizza.id}')

            if quantity_str and size_id:
                quantity = int(quantity_str)
                if quantity > 0:
                    pizza_size = PizzaSize.objects.get(id=size_id)

                    OrderPizza.objects.create(
                        order=order,
                        pizza=pizza,
                        quantity=quantity,
                        price_at_time=pizza_size.price
                    )
                    total += pizza_size.price * quantity
                    print(f"Added {quantity}x {pizza.name} to order {order.id}")

        # Save total
        order.total = total
        order.save()

        return render(request, 'confirmation.html', {
            'customer': customer,
            'order_items': order.orderpizza_set.all(),
            'total': total
        })

    # GET request: show order form
    return render(request, 'order.html', {'pizzas': pizzas})

def add_to_cart(request):
    if request.method == 'POST':
        pizza_id = request.POST.get('pizza_id')
        size_id = request.POST.get('size_id')
        quantity = int(request.POST.get('quantity'))

        pizza_size = PizzaSize.objects.get(id=size_id)

        item = {
            'pizza_id': pizza_id,
            'pizza_name': pizza_size.pizza.name,
            'size_id': size_id,
            'size_label': pizza_size.get_size_display(),
            'price': float(pizza_size.price),
            'quantity': quantity
        }

        cart = request.session.get('cart', [])
        cart.append(item)
        request.session['cart'] = cart

        messages.success(request, "🍕 Pizza added to cart!")
        return redirect('order')

    return redirect('menu')

def view_cart(request):
    cart = request.session.get('cart', [])
    total = sum(item['price'] * item['quantity'] for item in cart)
    return render(request, 'cart.html', {'cart': cart, 'total': total})

def clear_cart(request):
    request.session['cart'] = []
    return redirect('view_cart')

def checkout(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        address = request.POST['address']
        cart = request.session.get('cart', [])

        customer, _ = Customer.objects.get_or_create(
            email=email,
            defaults={'name': name, 'phone': phone, 'address': address}
        )

        order = Order.objects.create(customer=customer, total=0)
        total = 0

        for item in cart:
            pizza_size = PizzaSize.objects.get(id=item['size_id'])
            quantity = int(item['quantity'])
            subtotal = pizza_size.price * quantity
            total += subtotal

            OrderPizza.objects.create(
                order=order,
                pizza=pizza_size.pizza,
                quantity=quantity,
                price_at_time=pizza_size.price
            )

        order.total = total
        order.save()

        request.session['cart'] = []
        return redirect(reverse('order_confirmation', args=[order.id]))

    return redirect('view_cart')

def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order_items = order.orderpizza_set.select_related('pizza').all()
    total = sum(item.price_at_time * item.quantity for item in order_items)

    return render(request, 'confirmation.html', {
        'order': order,
        'order_items': order_items,
        'total': total,
        'customer': order.customer,
    })

def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:
            return render(request, "register.html", {"error": "Passwords do not match"})

        user = User.objects.create_user(username=username, email=email, password=password1)

        # Create the customer profile
        Customer.objects.create(
            user=user,
            name=username,  # Or any default
            email=email,
            phone='',
            address=''
        )

        login(request, user)
        return redirect('home')

    return render(request, "register.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect(request.GET.get("next", "home"))
        else:
            return render(request, "login.html", {
                "username": username,
                "error": "Wrong password"
            })

    return render(request, "login.html")


@login_required
def my_page(request):
    try:
        customer = request.user.customer_profile
        orders = Order.objects.filter(customer=customer).order_by('-created_at')
    except Customer.DoesNotExist:
        customer = None
        orders = []

    return render(request, 'my_page.html', {
        'orders': orders,
        'customer': customer,
        'user': request.user
    })