from django.shortcuts import render, redirect, get_object_or_404
import requests
import json
from .models import Dish, Cart, Order, CartItems, OrderItems
from .serializers import DishSerializer, UserSerializer
from django.core.paginator import Paginator
from .forms import CartAddProductForm
# from .cart import Cart
from django.contrib import auth, messages
from datetime import date

from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseBadRequest

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
    return render(request, 'foodcourt.html')

def order_details(request):
    """View function for foodcourt page of site."""
    # Render the HTML template index.html with the data in the context variable
    obj = []
    total_price = 0
    orders = Order.objects.filter(user=request.user)
    for order in orders:
        for i in order.order_item.all():     
            obj.append({
                "name": i.items.name,
                "unit_price": i.items.price,
                "price": i.price,
                "quantity": i.quantity
                })
        total_price += order.total_price    
    return render(request, 'order_details.html', {'order':obj,'total_price': total_price})


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


def make_pagination_html(current_page, total_pages):

    pagination_string = ""

    if current_page > 1:

        pagination_string += '<a href="?page=%s">previous</a>' % (current_page -1)

    pagination_string += '<span class="current"> Page %s of %s </span>' %(current_page, total_pages)

    if current_page < total_pages:

        pagination_string += '<a href="?page=%s">next</a>' % (current_page + 1)

    return pagination_string


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
    total_records = len(serializer.data)
    total_pages = total_records / 5
    pagination = make_pagination_html(current_page, total_pages)

    if total_records % 5 != 0:

        total_pages += 1 # adding one more page if the last page will contains less contacts 

        pagination = make_pagination_html(current_page, total_pages)

    return render(request, 'restaurant_details.html',{"menu_details":serializer.data,"restaurant": data['name'],"cart_product_form":CartAddProductForm()})

def get_restaurant(request):
    """View function for get Restaurant."""
    # Render the HTML template index.html with the data in the context variable
   
    url = "https://developers.zomato.com/api/v2.1/restaurant"
    querystring = {
        "res_id":request.GET['res_id'],
    }
    headers = {
        'user-key': "84fd63575a12f6a5537b8cf51215dca3",
        'content-type': "application/json"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    data = json.loads(response.text)
    
    return render(request, 'restaurant_details.html',{"restaurant_details":data})

# @require_POST
# def cart_add(request, product_id):
#     obj = []
#     total_price = 0
#     form = CartAddProductForm(request.POST)
#     if form.is_valid():
#         cd = form.cleaned_data
#         cart,created = Cart.objects.get_or_create(user=request.user)
#         product = get_object_or_404(Dish, id=product_id)
#         cart_item, created = CartItems.objects.get_or_create(
#                             user=request.user,
#                             items=product)
#         if not created:
#             cart_item.quantity += cd['quantity']
#             cart_item.cart = cart
#             cart_item.save()
#         else:
#             cart_item.quantity = cd['quantity']
#             cart_item.cart = cart
#             cart_item.save()
#         cart_item.price = cart_item.quantity * product.price
#         cart_item.save()
        
#         for i in cart.cart_item.all():
#             obj.append({
#                 "name": i.items.name,
#                 "unit_price": i.items.price,
#                 "price": i.price,
#                 "quantity": i.quantity
#                 })
#             total_price += i.price
#         cart.total_price = total_price
#         cart.save()
#     return render(request, 'cart_details.html', {'cart': obj,'cart_id': cart.id,'total_price': total_price})

@csrf_exempt
@require_POST
def cart_add(request):
    obj = []
    total_price = 0
    print ("jjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjj", request.POST)
    data = request.POST.get('data')
    products = json.loads(data)
    print ("mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm", products)
    cart,created = Cart.objects.get_or_create(user=request.user)
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
        # obj.append({
        #     "name": i.items.name,
        #     "unit_price": i.items.price,
        #     "price": i.price,
        #     "quantity": i.quantity
        #     })
        total_price += i.price
    cart.total_price = total_price
    cart.save()

    # obj = []
    # total_price = 0
    # form = CartAddProductForm(request.POST)
    # if form.is_valid():
    #     cd = form.cleaned_data
    #     cart,created = Cart.objects.get_or_create(user=request.user)
    #     product = get_object_or_404(Dish, id=product_id)
    #     cart_item, created = CartItems.objects.get_or_create(
    #                         user=request.user,
    #                         items=product)
    #     if not created:
    #         cart_item.quantity += cd['quantity']
    #         cart_item.cart = cart
    #         cart_item.save()
    #     else:
    #         cart_item.quantity = cd['quantity']
    #         cart_item.cart = cart
    #         cart_item.save()
    #     cart_item.price = cart_item.quantity * product.price
    #     cart_item.save()
        
    #     for i in cart.cart_item.all():
    #         obj.append({
    #             "name": i.items.name,
    #             "unit_price": i.items.price,
    #             "price": i.price,
    #             "quantity": i.quantity
    #             })
    #         total_price += i.price
    #     cart.total_price = total_price
    #     cart.save()
    print("kkkkkkkkkkkkkkkkkkkkkkkkkk", obj, cart.id, total_price)
    return HttpResponse(json.dumps(cart.id), content_type='application/json')
    # return render(request, 'cart_details.html', {'cart_id': cart.id})

def cart_details(request,cart_id):
    """View function for Cart Details page of site."""
    # Render the HTML template index.html with the data in the context variable
    cart = get_object_or_404(Cart, id=cart_id)
    for i in cart.cart_item.all():
        obj.append({
            "name": i.items.name,
            "unit_price": i.items.price,
            "price": i.price,
            "quantity": i.quantity
            })
    return render(request, 'cart_details.html', {'cart': obj,'cart_id': cart.id,'total_price': cart.total_price})

@require_POST
def place_order(request, cart_id):
    cart = get_object_or_404(Cart, id=cart_id)
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
    obj =[]
    for i in order.order_item.all():     
        obj.append({
            "name": i.items.name,
            "unit_price": i.items.price,
            "price": i.price,
            "quantity": i.quantity
            })
    return render(request, 'order_details.html', {'order': obj, 'total_price': order.total_price})