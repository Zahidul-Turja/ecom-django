from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import datetime

from .models import *

# Create your views here.


def store(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
        items = order.orderitem_set.all()  # type: ignore
        cartItems = order.get_cart_items
    else:
        items = []
        order = {
            "get_cart_total": 0,
            "get_cart_item": 0,
            "shipping": False,
        }
        cartItems = order["get_cart_item"]

    products = Product.objects.all()
    context = {
        "products": products,
        "cartItems": cartItems,
    }
    return render(request, "store/store.html", context)


def cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
        items = order.orderitem_set.all()  # type: ignore
        cartItems = order.get_cart_items
    else:
        try:
            cart = json.loads(request.COOKIES["cart"])
        except:
            cart = {}
        print("cart", cart)
        order = {
            "get_cart_total": 0,
            "get_cart_item": 0,
            "shipping": False,
        }
        items = []
        cartItems = order["get_cart_item"]

        for i in cart:
            cartItems += cart[i]["quantity"]

            product = Product.objects.get(id=i)
            total = (product.price * cart[i]["quantity"])

            order["get_cart_total"] += total
            order["get_cart_item"] += cart[i]["quantity"]

            item = {
                "product": {
                    "id": product.id,  # type: ignore
                    "name": product.name,
                    "price": product.price,
                    "image": product.image
                },
                "quantity": cart[i]["quantity"],
                "get_total": total,
            }
            items.append(item)

    context = {
        "items": items,
        "order": order,
        "cartItems": cartItems
    }
    return render(request, "store/cart.html", context)


def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
        items = order.orderitem_set.all()  # type: ignore
        cartItems = order.get_cart_items
    else:
        order = {
            "get_cart_total": 0,
            "get_cart_item": 0,
            "shipping": False,
        }
        items = []
        cartItems = order["get_cart_item"]

    context = {
        "items": items,
        "order": order,
        "cartItems": cartItems
    }
    return render(request, "store/checkout.html", context)


def updateItem(request):
    data = json.loads(request.body)
    productId = data["productId"]
    action = data["action"]

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(
        customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(
        order=order, product=product)

    if action == "add":
        orderItem.quantity = orderItem.quantity + 1  # type: ignore
    elif action == "remove":
        orderItem.quantity = orderItem.quantity - 1  # type: ignore
    orderItem.save()

    if orderItem.quantity <= 0:  # type: ignore
        orderItem.delete()

    return JsonResponse("Item added", safe=False)


# @csrf_exempt
def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
        total = float(data["form"]["total"])
        order.transaction_id = transaction_id  # type: ignore

        if total == order.get_cart_total:
            order.complete = True
        order.save()

        if order.shipping:
            ShippingAddress.objects.create(
                customer=customer,
                order=order,
                address=data["shipping"]["address"],
                city=data["shipping"]["city"],
                state=data["shipping"]["state"],
                zipcode=data["shipping"]["zipcode"],
            )
    else:
        print("User not logged in")
    return JsonResponse("Payment Complete", safe=False)
