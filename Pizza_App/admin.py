from django.contrib import admin
from .models import (
    Category, Order, OrderPizza, Customer,
    Pizza, PizzaSize, OrderPizzaTopping, Topping, Drink, OrderDrink
)
from django.utils.html import format_html
from django.urls import reverse

admin.site.register(Category)
admin.site.register(Pizza)
admin.site.register(PizzaSize)
admin.site.register(Drink)
admin.site.register(OrderDrink)

@admin.register(Topping)
class ToppingAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')


class OrderPizzaInline(admin.TabularInline):
    model = OrderPizza
    extra = 0
    show_change_link = True
    readonly_fields = ('pizza', 'quantity', 'price_at_time', 'special_instructions', 'toppings_display')

    def toppings_display(self, obj):
        return ", ".join([t.name for t in obj.toppings.all()])
    toppings_display.short_description = "Toppings"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'total', 'created_at', 'status')
    list_filter = ('status', 'created_at')
    search_fields = ('customer__name', 'customer__email')
    list_editable = ('status',)
    inlines = [OrderPizzaInline]
    ordering = ('-created_at',)

    actions = ['mark_completed', 'mark_cancelled']

    @admin.action(description="Mark selected orders as COMPLETED")
    def mark_completed(self, request, queryset):
        updated = queryset.update(status='COMPLETED')
        self.message_user(request, f"{updated} order(s) marked as COMPLETED.")

    @admin.action(description="Mark selected orders as CANCELLED")
    def mark_cancelled(self, request, queryset):
        updated = queryset.update(status='CANCELLED')
        self.message_user(request, f"{updated} order(s) marked as CANCELLED.")


@admin.register(OrderPizza)
class OrderPizzaAdmin(admin.ModelAdmin):
    list_display = ('order', 'pizza', 'quantity', 'price_at_time', 'special_instructions', 'toppings_display')
    readonly_fields = ('order', 'pizza', 'quantity', 'price_at_time', 'special_instructions', 'toppings_display')

    def toppings_display(self, obj):
        return ", ".join([t.name for t in obj.toppings.all()])
    toppings_display.short_description = "Toppings"

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'order_count', 'view_orders_link')
    search_fields = ('name', 'email')
    readonly_fields = ('user', 'order_summary')

    def order_count(self, obj):
        return obj.order_set.count()
    order_count.short_description = "Orders"

    def view_orders_link(self, obj):
        url = reverse("admin:Pizza_App_order_changelist") + f"?customer__id__exact={obj.id}"
        return format_html('<a href="{}">View Orders</a>', url)
    view_orders_link.short_description = "Orders Link"

    def order_summary(self, obj):
        orders = obj.order_set.all()
        if not orders:
            return "No orders."
        return format_html("<ul>{}</ul>", "".join([
            f"<li>Order #{o.id} - {o.get_status_display()} - {o.created_at.strftime('%Y-%m-%d')}</li>"
            for o in orders
        ]))
    order_summary.short_description = "Order Summary"