"""foodcourt URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import url, include
from restaurant.views import *

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$',home,name='home'),
	url(r'^home',foodcourt,name='foodcourt'),
    url(r'^foodcourt/restaurants',
    	search_restaurants,
    	name='search_restaurants'),
    url(r'foodcourt/restaurant-details',
    	get_foodmenu_details,
    	name='get_foodmenu_details'),
    # url(r'^add/(?P<product_id>\d+)/$', cart_add, name='cart_add'),
    url(r'^foodcourt/cart-add', cart_add, name='cart_add'),
    url(
        r'foodcourt/cart-details',
        cart_details,
        name='cart_details'
    ),
    # url(r'^foodcourt/cart-details/(?P<id>\d+)/$', cart_details, name='cart_details'),
    url(r'^foodcourt/place-order/(?P<cart_id>\d+)/$', place_order, name='place_order'),
    url(r'^foodcourt/order-details', order_details, name='order_details'),
    url(r'^foodcourt/signup', user_signup, name='user_signup'),
    url(r'^foodcourt/user-registration', user_registration, name='user_registration'),
    url(r'^foodcourt/login', user_login, name='user_login'),
    url(r'^foodcourt/users', user_authenticate, name='user_authenticate'), 
    url(r'^foodcourt/logout', logout, name='logout'),

    url('api/login', login),
    url(
        r'restaurant-search/$',
        RestaurantList.as_view(),
        name='restaurant-search'
    ),
    url(
        r'food-menu-list/$',
        FoodMenuList.as_view(),
        name='food-menu-list'
    ),

    url(
        r'orders/$',
        OrderView.as_view(),
        name='orders'
    ),

    url(
        r'cart/$',
        CartView.as_view(),
        name='cart'
    ),
]
