from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from django.template.loader import render_to_string
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .models import Pizza, Order, Customer, OrderPizza, PizzaSize, Topping, OrderPizzaTopping, Drink, OrderDrink
from django.views.decorators.http import require_POST
from django.core.mail import send_mail


def home(request):
    return render(request, 'Pizza_App/home.html')

def about_us(request):
    return render (request, 'aboutus.html')


def menu(request):
    pizzas = Pizza.objects.all()
    sizes = PizzaSize.objects.all()
    toppings = Topping.objects.all()
    drinks = Drink.objects.all() 
    
    return render(request, 'menu.html', {
        'pizzas': pizzas,
        'sizes': sizes,
        'toppings': toppings,
        'drinks': drinks 
    })

def order(request):
    pizzas = Pizza.objects.all()
    toppings = Topping.objects.all()
    drinks = Drink.objects.all()

    if request.method == "POST":
        customer_name = request.POST['name']
        customer_email = request.POST['email']
        customer_phone = request.POST['phone']
        customer_address = request.POST['address']

        customer, _ = Customer.objects.get_or_create(
            email=customer_email,
            defaults={
                'name': customer_name,
                'phone': customer_phone,
                'address': customer_address
            }
        )

        order = Order.objects.create(customer=customer, total=0)
        total = 0

        for pizza in pizzas:
            quantity_str = request.POST.get(f'quantity_{pizza.id}')
            size_id = request.POST.get(f'pizza_size_id_{pizza.id}')
            toppings_ids = request.POST.getlist(f'toppings_{pizza.id}')
            instructions = request.POST.get(f'instructions_{pizza.id}', '')

            if quantity_str and size_id:
                quantity = int(quantity_str)
                if quantity > 0:
                    pizza_size = PizzaSize.objects.get(id=size_id)
                    toppings_objs = Topping.objects.filter(id__in=toppings_ids)
                    toppings_total = sum(t.price for t in toppings_objs)
                    price = pizza_size.price + toppings_total

                    order_pizza = OrderPizza.objects.create(
                        order=order,
                        pizza=pizza,
                        size=pizza_size,
                        quantity=quantity,
                        price_at_time=price,
                        special_instructions=instructions
                    )

                    for topping in toppings_objs:
                        OrderPizzaTopping.objects.create(order_pizza=order_pizza, topping=topping)

                    total += price * quantity
                    print(f"Added {quantity}x {pizza.name} to order {order.id}")

            for drink in Drink.objects.all():
                 if f"drink_selected_{drink.id}" in request.POST:
                    qty = int(request.POST.get(f"drink_quantity_{drink.id}", 1))
                    if qty > 0:
                        OrderDrink.objects.create(order=order, drink=drink, quantity=qty)
                        total += drink.price * qty

        order.total = total
        order.save()

        return render(request, 'confirmation.html', {
            'customer': customer,
            'order_items': order.orderpizza_set.all(),
            'order_drinks': order.orderdrink_set.all(),
            'total': total
        })

    return render(request, 'order.html', {'pizzas': pizzas, 'toppings': toppings, 'drinks' : drinks})


def add_to_cart(request):
    print("POST drink_id:", request.POST.get("drink_id"))

    if request.method == 'POST':

        if 'drink_id' in request.POST:
            drink_id = request.POST.get('drink_id')
            quantity = int(request.POST.get('quantity', 1))

            try:
                drink = Drink.objects.get(id=drink_id)
            except Drink.DoesNotExist:
                messages.error(request, "Drink not found.")
                return redirect('order')

            cart_drinks = request.session.get('cart_drinks', [])
            for d in cart_drinks:
                if d.get('drink_id') == drink.id:
                    d['quantity'] += quantity
                    break
            else:
                cart_drinks.append({
                    'drink_id': drink.id, 
                    'name': drink.name,
                    'price': float(drink.price),
                    'quantity': quantity
                })

            request.session['cart_drinks'] = cart_drinks
            messages.success(request, f"🥤 {drink.name} added to cart!")
            return redirect('order')

        if 'pizza_id' in request.POST and 'size_id' in request.POST:
            pizza_id = request.POST.get('pizza_id')
            size_id = request.POST.get('size_id')
            quantity = int(request.POST.get('quantity'))
            topping_ids = request.POST.getlist('toppings')
            instructions = request.POST.get('instructions', '')

            try:
                pizza_size = PizzaSize.objects.get(id=size_id)
            except PizzaSize.DoesNotExist:
                messages.error(request, "Pizza size not found.")
                return redirect('order')

            size_label = pizza_size.get_size_display()
            if size_label == "Small":
                topping_price = 10
            elif size_label == "Medium":
                topping_price = 20
            elif size_label == "Large":
                topping_price = 30
            else:
                topping_price = 10 

            selected_toppings = Topping.objects.filter(id__in=topping_ids)
            toppings_list = [{'id': t.id, 'name': t.name, 'price': topping_price} for t in selected_toppings]
            toppings_total = topping_price * len(toppings_list)

            item = {
                'pizza_id': pizza_id,
                'pizza_name': pizza_size.pizza.name,
                'size_id': size_id,
                'size_label': size_label,
                'price': float(pizza_size.price) + toppings_total,
                'toppings': toppings_list,
                'quantity': quantity,
                'instructions': instructions
            }

            cart = request.session.get('cart', [])
            for existing in cart:
                if (
                    existing['pizza_id'] == item['pizza_id'] and
                    existing['size_id'] == item['size_id'] and
                    existing['toppings'] == item['toppings'] and
                    existing['instructions'] == item['instructions']
                ):
                    existing['quantity'] += item['quantity']
                    break
            else:
                cart.append(item)

            request.session['cart'] = cart
            messages.success(request, f"🍕 {pizza_size.pizza.name} added to cart!")
            return redirect('order')

    return redirect('menu')


def view_cart(request):
    cart = request.session.get('cart', [])
    cart_drinks = request.session.get('cart_drinks', [])

    total = sum(item['price'] * item['quantity'] for item in cart)
    total += sum(drink['price'] * drink['quantity'] for drink in cart_drinks)

    return render(request, 'cart.html', {
        'cart': cart,
        'cart_drinks': cart_drinks,
        'total': total
    })


def clear_cart(request):
    request.session['cart'] = []
    request.session ['cart_drinks'] = []
    return redirect('view_cart')


def checkout(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        address = request.POST['address']
        cart = request.session.get('cart', [])
        cart_drinks = request.session.get('cart_drinks', [])

        customer, _ = Customer.objects.get_or_create(
            email=email,
            defaults={'name': name, 'phone': phone, 'address': address}
        )

        order = Order.objects.create(customer=customer, total=0)
        total = 0

        for item in cart:
            pizza_size = PizzaSize.objects.get(id=item['size_id'])
            quantity = item['quantity']
            price = item['price']
            instructions = item.get('instructions', '')

            order_pizza = OrderPizza.objects.create(
                order=order,
                pizza=pizza_size.pizza,
                size=pizza_size,
                quantity=quantity,
                price_at_time=price,
                special_instructions=instructions
            )

            for topping_data in item.get('toppings', []):
                topping = Topping.objects.get(id=topping_data['id'])
                OrderPizzaTopping.objects.create(order_pizza=order_pizza, topping=topping)

            total += price * quantity

        for item in cart_drinks:
            drink = Drink.objects.get(id=item['drink_id'])
            quantity = item['quantity']
            price = item['price']

            OrderDrink.objects.create(
                order=order,
                drink=drink,
                quantity=quantity,
                price_at_time=price
            )

            total += price * quantity

        order.total = total
        order.save()

        request.session['cart'] = []
        request.session['cart_drinks'] = []

        order_items = order.order_pizzas.select_related('pizza', 'size').prefetch_related('toppings')
        order_drinks = order.order_drinks.select_related('drink')

        for item in order_items:
            item.total_price = item.price_at_time * item.quantity

        for drink in order_drinks:
            drink.total_price = drink.price_at_time * drink.quantity

        email_context = {
            'order': order,
            'order_items': order_items,
            'order_drinks': order_drinks,
            'total': order.total,
            'customer': customer,
        }

        message = render_to_string('emails/order_confirmation_email.txt', email_context)

        send_mail(
            subject=f"🍕 Your The Pizzeria Order Confirmation (Order #{order.id})",
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[customer.email],
            fail_silently=False,
        )

        return redirect(reverse('order_confirmation', args=[order.id]))

    return redirect('view_cart')


def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order_items = order.order_pizzas.select_related('pizza', 'size').prefetch_related('toppings')
    order_drinks = order.order_drinks.select_related('drink')

    total = sum(item.price_at_time * item.quantity for item in order_items)
    total += sum(drink.price_at_time * drink.quantity for drink in order_drinks)

    return render(request, 'confirmation.html', {
        'order': order,
        'order_items': order_items,
        'order_drinks': order_drinks,
        'total': total,
        'customer': order.customer,
    })


def remove_pizza_from_cart(request, index):
    cart = request.session.get('cart', [])
    if 0 <= index < len(cart):
        del cart[index]
        request.session['cart'] = cart
        messages.success(request, "Pizza removed from cart.")
    return redirect('view_cart')


def remove_drink_from_cart(request, index):
    cart_drinks = request.session.get('cart_drinks', [])
    if 0 <= index < len(cart_drinks):
        del cart_drinks[index]
        request.session['cart_drinks'] = cart_drinks
        messages.success(request, "Drink removed from cart.")
    return redirect('view_cart')


@require_POST
def update_cart_quantity(request):
    item_type = request.POST.get('type') 
    index = int(request.POST.get('index'))
    quantity = int(request.POST.get('quantity'))

    if quantity < 1:
        messages.error(request, "Quantity must be at least 1.")
        return redirect('view_cart')

    if item_type == 'pizza':
        cart = request.session.get('cart', [])
        if 0 <= index < len(cart):
            cart[index]['quantity'] = quantity
            request.session['cart'] = cart
    elif item_type == 'drink':
        cart_drinks = request.session.get('cart_drinks', [])
        if 0 <= index < len(cart_drinks):
            cart_drinks[index]['quantity'] = quantity
            request.session['cart_drinks'] = cart_drinks

    messages.success(request, "Quantity updated.")
    return redirect('view_cart')

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

def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:
            return render(request, "register.html", {"error": "Passwords do not match"})

        user = User.objects.create_user(username=username, email=email, password=password1)

        Customer.objects.create(
            user=user,
            name=username,
            email=email,
            phone='',
            address=''
        )

        login(request, user)
        return redirect('home')

    return render(request, "register.html")

@login_required
def my_page(request):
    try:
        customer = request.user.customer_profile
        orders = Order.objects.filter(customer=customer).prefetch_related(
            'order_pizzas__pizza',
            'order_pizzas__size',
            'order_pizzas__toppings'
        ).order_by('-created_at')    
    
    except Customer.DoesNotExist:
        customer = None
        orders = []

    return render(request, 'my_page.html', {
        'orders': orders,
        'customer': customer,
        'user': request.user
    })

@login_required
def reorder(request, order_id):
    try:
        customer_profile = request.user.customer_profile
    except Customer.DoesNotExist:
        messages.error(request, "You don't have a customer profile.")
        return redirect('my_page')

    original_order = get_object_or_404(Order, id=order_id, customer=customer_profile)

    new_order = Order.objects.create(
        customer=customer_profile,
        total=0,
        status='PENDING'
    )

    for item in original_order.order_pizzas.all():
        new_item = OrderPizza.objects.create(
            order=new_order,
            pizza=item.pizza,
            quantity=item.quantity,
            size=item.size,
            price_at_time=item.price_at_time,
            special_instructions=item.special_instructions
        )

    for topping in item.toppings.all():
        OrderPizzaTopping.objects.create(
            order_pizza=new_item,
            topping=topping
        )

    for drink_item in original_order.order_drinks.all():
        OrderDrink.objects.create(
            order=new_order,
            drink=drink_item.drink,
            quantity=drink_item.quantity,
            price_at_time=drink_item.price_at_time
        )

    new_order.calculate_total()

    messages.success(request, f"Order #{original_order.id} reordered successfully.")
    return redirect('order_confirmation', order_id=new_order.id)
