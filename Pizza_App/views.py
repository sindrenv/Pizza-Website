from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User


from .models import Pizza, Order, Customer, OrderPizza, PizzaSize

def home(request):
    return render(request, 'Pizza_App/home.html')

def menu(request):
    pizzas = Pizza.objects.all()
    return render(request, 'menu.html', {'pizzas': pizzas})


def order(request):
    pizzas = Pizza.objects.all()

    if request.method == "POST":
        # ------------------------------
        # 🧍 Customer Information
        # ------------------------------
        customer_name = request.POST['name']
        customer_email = request.POST['email']
        customer_phone = request.POST['phone']
        customer_address = request.POST['address']

        # ------------------------------
        # 👤 Create or Find Customer
        # ------------------------------
        customer, created = Customer.objects.get_or_create(
            email=customer_email,
            defaults={
                'name': customer_name,
                'phone': customer_phone,
                'address': customer_address
            }
        )

        # ------------------------------
        # 🧾 Create Order
        # ------------------------------
        order = Order.objects.create(customer=customer, total=0)
        total = 0

        # ------------------------------
        # 🍕 Loop Through All Pizzas
        # ------------------------------
        for pizza in pizzas:
            quantity_str = request.POST.get(f'quantity_{pizza.id}')
            size_id = request.POST.get(f'pizza_size_id_{pizza.id}')

            if quantity_str and size_id:
                quantity = int(quantity_str)
                if quantity > 0:
                    pizza_size = PizzaSize.objects.get(id=size_id)

                    # ------------------------------
                    # 💾 Save OrderPizza
                    # ------------------------------
                    OrderPizza.objects.create(
                        order=order,
                        pizza=pizza,
                        quantity=quantity,
                        price_at_time=pizza_size.price
                    )

                    # 💰 Update Total
                    total += pizza_size.price * quantity

        # ------------------------------
        # 💳 Save Final Total to Order
        # ------------------------------
        order.total = total
        order.save()

        # ------------------------------
        # ✅ Show Confirmation Page
        # ------------------------------
        return render(request, 'confirmation.html', {
            'customer': customer,
            'order_items': order.orderpizza_set.all(),
            'total': total
        })

    # ------------------------------
    # 🌐 Initial Page Load (GET)
    # ------------------------------
    return render(request, 'order.html', {'pizzas': pizzas})

def confirmation(request):
    return render(request, 'confirmation.html')

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

        return redirect('view_cart')

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

        customer, created = Customer.objects.get_or_create(
            email=email,
            defaults={'name': name, 'phone': phone, 'address': address}
        )

        order = Order.objects.create(customer=customer, total=0)
        total = 0

        for item in cart:
            pizza_size = PizzaSize.objects.get(id=item['size_id'])
            quantity = int(item['quantity'])
            total += pizza_size.price * quantity

            OrderPizza.objects.create(
                order=order,
                pizza=pizza_size.pizza,
                quantity=quantity,
                price_at_time=pizza_size.price
            )

        order.total = total
        order.save()

        request.session['cart'] = []  # Clear cart

        return render(request, 'confirmation.html', {'order': order})

    return redirect('view_cart')


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
