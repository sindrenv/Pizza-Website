"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from Pizza_App import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', views.home, name='home'),
    path('menu/', views.menu, name='menu'),
    path('order/', views.order, name='order'),
    path('about/', views.about_us, name='about'),    
    path('confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),

    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),

    path('my-page/', views.my_page, name='my_page'),
    path('reorder/<int:order_id>/', views.reorder, name='reorder'),
    path('order/confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    

    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('clear-cart/', views.clear_cart, name='clear_cart'),
    path('remove-from-cart/pizza/<int:index>/', views.remove_pizza_from_cart, name='remove_pizza_from_cart'),
    path('remove-from-cart/drink/<int:index>/', views.remove_drink_from_cart, name='remove_drink_from_cart'),
    path('update-cart-quantity/', views.update_cart_quantity, name='update_cart_quantity'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
