from django.shortcuts import render, redirect, get_object_or_404
import requests
import json
from .models import Dish, Cart, Order, CartItems, OrderItems
from .serializers import DishSerializer, UserSerializer
from django.core.paginator import Paginator
from django.contrib import auth, messages
from datetime import date

from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseBadRequest


# Signup View
def user_registration(request):
    errors = {}
    if request.method == 'POST':
        if not request.POST['email']:
            errors = {'email':'Email is required'}
        elif not request.POST['password1']:
            errors = {'email':'password is required'}
        if User.objects.filter(email=request.POST['email']).count():
            errors = {'email':'Email already exist'}
        elif request.POST['password1'] != request.POST['password2']:
            errors = {'password':'Password not matched'}
        else:
            user = User.objects.create(email= request.POST['email'], username= str(request.POST['email']))
            user.set_password(request.POST['password1'])
            user.save()
            user1 = auth.authenticate(username=request.POST['email'], password=request.POST['password1'])
            if user1 is not None:
                # correct username and password login the user
                auth.login(request, user1)
                return redirect('foodcourt')
    return render(request, 'signup.html', {'errors': errors})

# User Authentication View
def user_authenticate(request):
    if request.user.is_authenticated():
        return redirect('foodcourt')
 
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = auth.authenticate(username=email, password=password)
        if user is not None:
            # correct username and password login the user
            auth.login(request, user)
            return redirect('foodcourt')
 
        else:
            messages.error(request, 'Error wrong username/password')
 
    return render(request, 'login.html')

def home(request):
    """View function for home page of site."""
    # Render the HTML template index.html with the data in the context variable
    return render(request, 'home.html')

def user_signup(request):
    """View function for login page of site."""
    # Render the HTML template index.html with the data in the context variable
    return render(request, 'signup.html')

def user_login(request):
    """View function for login page of site."""
    # Render the HTML template index.html with the data in the context variable
    return render(request, 'login.html')

def logout(request):
    auth.logout(request)
    return render(request,'logout.html')

def foodcourt(request):
    """View function for foodcourt page of site."""
    # Render the HTML template index.html with the data in the context variable
    context = {"foodcourt_page": "active"}
    return render(request, 'foodcourt.html', context)

# User Order Details View
def order_details(request):
    """View function for foodcourt page of site."""
    # Render the HTML template index.html with the data in the context variable
    obj = []
    total_price = 0
    orders = Order.objects.filter(user=request.user).order_by('-id')
    for order in orders:
        for i in order.order_item.all():     
            obj.append({
                "id": order.id,
                "name": i.items.name,
                "unit_price": i.items.price,
                "price": i.price,
                "quantity": i.quantity
                })
        total_price += order.total_price
    context = {"order_page": "active", 'order':obj,'total_price': total_price}    
    return render(request, 'order_details.html', context)

# Search Restaurants View
def search_restaurants(request):
    """View function for Search Restaurant."""
    # Render the HTML template index.html with the data in the context variable
    current_page = request.GET.get('page',1)
    offset = (int(current_page) - 1) * 5 + 1

    url = "https://developers.zomato.com/api/v2.1/search"
    querystring = {
        "q":request.GET['search'],
        "start": offset,
        "count": 5
    }
    headers = {
        'user-key': "84fd63575a12f6a5537b8cf51215dca3",
        'content-type': "application/json"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    data = json.loads(response.text)

    total_pages = data['results_found'] / 5
    
    pagination = {
        'total_pages': round(total_pages),
        'current_page': current_page,
        'next': int(current_page)+1,
        'search': request.GET['search'], 
        'previous': int(current_page)-1
    }

    if  data['results_found'] % 5 != 0:

        total_pages += 1 # adding one more page if the last page will contains less contacts 

        pagination = {
            'total_pages': round(total_pages),
            'current_page': current_page,
            'next': int(current_page)+1,
            'search': request.GET['search'],
            'previous': int(current_page)-1
        }


    return render(request, 'foodcourt.html', {"restaurants":data['restaurants'], 'pagination': pagination})

# Food Menu Details View
def get_foodmenu_details(request):
    """View function for get Restaurant."""
    # Render the HTML template index.html with the data in the context variable
    current_page = request.GET.get('page' ,1)
    limit = 5 * current_page
    offset = limit - 5

    url = "https://developers.zomato.com/api/v2.1/restaurant"
    querystring = {
        "res_id":request.GET['res_id'],
    }
    headers = {
        'user-key': "84fd63575a12f6a5537b8cf51215dca3",
        'content-type': "application/json"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    menu_list = Dish.objects.filter(restaurant=1)
    serializer = DishSerializer(
            Dish.objects.filter(restaurant=1), many=True
        )
    data = json.loads(response.text)

    return render(request, 'restaurant_details.html',{"menu_details":serializer.data,"restaurant": data['name'],"restaurant_id":request.GET['res_id']})

# def get_restaurant(request):
#     """View function for get Restaurant."""
#     # Render the HTML template index.html with the data in the context variable
   
#     url = "https://developers.zomato.com/api/v2.1/restaurant"
#     querystring = {
#         "res_id":request.GET['res_id'],
#     }
#     headers = {
#         'user-key': "84fd63575a12f6a5537b8cf51215dca3",
#         'content-type': "application/json"
#     }

#     response = requests.request("GET", url, headers=headers, params=querystring)
#     data = json.loads(response.text)
    
#     return render(request, 'restaurant_details.html',{"restaurant_details":data})

# Add items into the cart
@csrf_exempt
@require_POST
def cart_add(request):
    obj = []
    total_price = 0

    data = request.POST.get('data')
    products = json.loads(data)
    restaurant = json.loads(request.POST.get('restaurant'))

    cart,created = Cart.objects.get_or_create(user=request.user)
    if not created:
        if cart.restaurant != restaurant:
            cart.cart_item.all().delete()

    for p in products:
        product = get_object_or_404(Dish, id=p['product_id'])
        cart_item, created = CartItems.objects.get_or_create(
                            user=request.user,
                            items=product)
        if not created:
            cart_item.quantity = cart_item.quantity+int(p['quantity']) if cart_item.quantity != None else int(p['quantity'])
            cart_item.cart = cart
            cart_item.save()
        else:
            cart_item.quantity = int(p['quantity'])
            cart_item.cart = cart
            cart_item.save()

        cart_item.price = cart_item.quantity * product.price
        cart_item.save()
        
    for i in cart.cart_item.all():
        total_price += i.price
    cart.total_price = total_price
    cart.restaurant = restaurant
    cart.save()

    return HttpResponse(json.dumps(cart.id), content_type='application/json')


# Cart Details View
def cart_details(request):
    """View function for Cart Details page of site."""
    # Render the HTML template index.html with the data in the context variable
    obj = []
    try:
        try:
            cart = Cart.objects.get(id=request.GET['cart_id'])
            for i in cart.cart_item.all():
                obj.append({
                    "name": i.items.name,
                    "unit_price": i.items.price,
                    "price": i.price,
                    "quantity": i.quantity
                    })
        except Cart.DoesNotExist:
            return render(request, 'cart_details.html', {'cart': obj})
    except:
        try:
            cart = Cart.objects.get(user=request.user)
            for i in cart.cart_item.all():
                obj.append({
                    "name": i.items.name,
                    "unit_price": i.items.price,
                    "price": i.price,
                    "quantity": i.quantity
                    })
        except Cart.DoesNotExist:
            return render(request, 'cart_details.html', {'cart': obj})
    context = {"cart_page": "active", 'cart': obj,'cart_id': cart.id,'total_price': cart.total_price} 
    return render(request, 'cart_details.html', context)

# Place Order View
@require_POST
def place_order(request, cart_id):
    obj =[]
    try:
        cart = Cart.objects.get(id=cart_id)
        order = Order.objects.create(user=request.user,order_date=date.today(),total_price=cart.total_price, restaurant=cart.restaurant)

        for i in cart.cart_item.all():
            OrderItems.objects.create(
                                user=request.user,
                                items=i.items,
                                order=order,
                                quantity=i.quantity,
                                price=i.price)

        cart.cart_item.all().delete()
        cart.delete()
        for i in order.order_item.all():     
            obj.append({
                "id": order.id,
                "name": i.items.name,
                "unit_price": i.items.price,
                "price": i.price,
                "quantity": i.quantity
                })
        messages.success(request, 'Your Order Plcaed Successfully!!!!!')
    except Cart.DoesNotExist:
        return render(request, 'cart_details.html', {'cart': obj})
    context = {"order_page": "active", 'order': obj, 'total_price': order.total_price}
    return render(request, 'order_details.html', context)