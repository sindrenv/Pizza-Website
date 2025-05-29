from django.contrib import admin
from .models import (
    Category, Order, OrderPizza, Customer,
    Pizza, PizzaSize, OrderPizzaTopping, Topping
)

# Registro simple
admin.site.register(Category)
admin.site.register(Customer)
admin.site.register(Pizza)
admin.site.register(PizzaSize)
admin.site.register(OrderPizzaTopping)  # Este no estaba, pero lo puedes registrar si quieres verlo también

# Toppings
@admin.register(Topping)
class ToppingAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')

# Inline para mostrar pizzas dentro de una orden
class OrderPizzaInline(admin.TabularInline):
    model = OrderPizza
    extra = 0
    show_change_link = True
    readonly_fields = ('pizza', 'quantity', 'price_at_time', 'special_instructions', 'toppings_display')

    def toppings_display(self, obj):
        return ", ".join([t.name for t in obj.toppings.all()])
    toppings_display.short_description = "Toppings"

# Admin de orden
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('customer', 'total', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('customer__name', 'customer__email')
    inlines = [OrderPizzaInline]

# Admin de cada pizza dentro de una orden
@admin.register(OrderPizza)
class OrderPizzaAdmin(admin.ModelAdmin):
    list_display = ('order', 'pizza', 'quantity', 'price_at_time', 'special_instructions', 'toppings_display')
    readonly_fields = ('order', 'pizza', 'quantity', 'price_at_time', 'special_instructions', 'toppings_display')

    def toppings_display(self, obj):
        return ", ".join([t.name for t in obj.toppings.all()])
    toppings_display.short_description = "Toppings"
