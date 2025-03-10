from django.shortcuts import render
from .models import MenuItem  # Import your model

def menu_list(request):
    menu_items = MenuItem.objects.all()  # Fetch menu items from DB
    return render(request, 'menu/menu_list.html', {'menu_items': menu_items})
