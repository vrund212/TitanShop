from django.contrib import messages
from django.contrib.auth.decorators import login_required

from django.db.models import Sum
from django.forms import ModelForm
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_POST

from .models import ShopCart, ShopCartForm, OrderForm, Order, OrderDetail
from shop.models import PromoCode


# Create your views here.
@login_required(login_url='/shop/login/')
def index(request):
    current_user = request.user
    orders = Order.objects.filter(user_id=current_user.id).order_by('-create_at')
    order_summaries = []
    for order in orders:
        item_count = OrderDetail.objects.filter(order_id=order.id).count()
        order_summaries.append({
            'order': order,
            'item_count': item_count,
        })

    context = {'page': 'orders',
               'orders': orders,
               'order_summaries': order_summaries,
               }
    return render(request, 'order_list.html', context)


@login_required(login_url='/shop/login/')
def shop_cart_list(request):
    current_user = request.user
    shopcart = ShopCart.objects.all().filter(user_id=current_user.id)
    carttotal = 0
    for rs in shopcart:
        carttotal += rs.quantity * rs.product.discount_price

    promo_code = None
    discount_percent = 0
    discount_amount = 0
    final_total = carttotal
    if 'promo_code' in request.session:
        promo_code = request.session.get('promo_code')
        discount_percent = request.session.get('discount_percent', 0)
        discount_amount = (discount_percent / 100) * carttotal
        final_total = carttotal - discount_amount

    carttax = (14/100)*final_total
    cartwithtax = final_total + carttax

    context = {'page': 'cart',
               'shopcart': shopcart,
               'carttotal': carttotal,
               'carttax': carttax,
               'cartwithtax': cartwithtax,
               'promo_code': promo_code,
               'discount_percent': discount_percent,
               'discount_amount': discount_amount,
               }
    return render(request, 'shop_cart_list.html', context)


@login_required(login_url='/shop/login/')
def shop_cart_add(request, product_id):
    # if this is a POST request we need to process the form data
    url = request.META.get('HTTP_REFERER')  #
    # return HttpResponse(url)
    form = ShopCartForm(request.POST or None)
    if request.method == 'POST':
        # check whether it's valid:
        if form.is_valid():
            current_user = request.user  # Get User id
            quantity = form.cleaned_data['quantity']  # get product quantity from form

            # Checking product in ShopCart
            try:
                q1 = ShopCart.objects.get(user_id=current_user.id, product_id=product_id)
            except ShopCart.DoesNotExist:
                q1 = None
            if q1 != None:  # Update  quantity to exist product quantity
                q1.quantity = q1.quantity + quantity
                q1.save()
            else:  # Add new item to shop cart
                data = ShopCart(user_id=current_user.id, product_id=product_id, quantity=quantity)
                data.save()
            request.session['cart_items'] = ShopCart.objects.filter(
                user_id=current_user.id).count()  # Count item in shop cart
            messages.success(request, "Product added to cart.. ")
            return HttpResponseRedirect(url)

    return HttpResponseRedirect(reverse('shop:product_detail', args=[product_id]))


@login_required(login_url='/shop/login/')
def shop_cart_delete(request, id):
    url = request.META.get('HTTP_REFERER')  # Bir önceki adresi alır
    ShopCart.objects.filter(id=id).delete()
    messages.success(request, "Product deleted from  cart.. ")
    return HttpResponseRedirect(url)


@login_required(login_url='/shop/login/')
def shop_cart_checkout(request):
    current_user = request.user
    shopcart = ShopCart.objects.all().filter(user_id=current_user.id)
    carttotal = 0
    carttax = 0
    cartwithtax = 0
    discount_amount = 0
    discount_percent = 0
    final_total = 0
    promo_code = None
    
    for rs in shopcart:
        carttotal += rs.quantity * rs.product.discount_price
    
    # Check for applied promo code in session
    if 'promo_code' in request.session:
        promo_code = request.session.get('promo_code')
        discount_percent = request.session.get('discount_percent', 0)
        discount_amount = (discount_percent / 100) * carttotal
        final_total = carttotal - discount_amount
    else:
        final_total = carttotal
    
    carttax = (14 / 100) * final_total
    cartwithtax = final_total + carttax

    form = OrderForm(request.POST or None)
    if request.method == 'POST':
        # check whether it's valid:
        if form.is_valid():

            # Send Credit card information to bank and get result
            # If payment accepted continue else send payment error to checkout page

            data = Order()
            data.name = form.cleaned_data['name']  # get product quantity from form
            data.surname = form.cleaned_data['surname']
            data.address = form.cleaned_data['address']
            data.city = form.cleaned_data['city']
            data.phone = form.cleaned_data['phone']
            data.to = form.cleaned_data['name']
            data.user_id = current_user.id
            data.total = cartwithtax
            data.promo_code = promo_code
            data.discount_amount = discount_amount
            data.save()

            # Save Shopcart items to Order detail items
            for rs in shopcart:
                detail = OrderDetail()
                detail.order_id = data.id  # Order Id
                detail.product_id = rs.product_id
                detail.user_id = current_user.id
                # detail.quantity = rs.quantity
                detail.price = rs.product.price
                detail.total = rs.amount
                detail.save()
                #  Reduce product Amount  (quantity)

            ShopCart.objects.filter(user_id=current_user.id).delete()  # Clear & Delete shopcart
            request.session.pop('promo_code', None)  # Clear promo code from session
            request.session.pop('discount_percent', None)
            request.session['cart_items'] = 0
            messages.success(request, "Order has been completed. Thank You ")
            return HttpResponseRedirect("/order")

    context = {'page': 'checkout',
               'shopcart': shopcart,
               'carttotal': carttotal,
               'carttax': carttax,
               'cartwithtax': cartwithtax,
               'promo_code': promo_code,
               'discount_percent': discount_percent,
               'discount_amount': discount_amount,
               'final_total': final_total,
               }
    return render(request, 'shop_cart_checkout.html', context)


@login_required(login_url='/shop/login/')
def order_detail(request, id):
    order = get_object_or_404(Order, pk=id, user_id=request.user.id)
    items = OrderDetail.objects.filter(order=id).select_related('product')
    subtotal = sum(item.total for item in items)
    item_count = items.count()
    status_steps = ['New', 'Accepted', 'Preaparing', 'OnShipping', 'Completed']
    current_step = status_steps.index(order.status) if order.status in status_steps else -1

    context = {'page': 'detail',
               'order': order,
               'items': items,
               'subtotal': subtotal,
               'item_count': item_count,
               'status_steps': status_steps,
               'current_step': current_step,
               }
    return render(request, 'order_detail.html', context)


@require_POST
@login_required(login_url='/shop/login/')
def apply_promo_code(request):
    """Apply promo code and calculate discount"""
    code = request.POST.get('promo_code', '').strip()
    redirect_to = request.META.get('HTTP_REFERER', '/order/shopcart')

    if not code:
        request.session.pop('promo_code', None)
        request.session.pop('discount_percent', None)
        messages.error(request, 'Please enter a promo code.')
        return HttpResponseRedirect(redirect_to)

    try:
        promo = PromoCode.objects.get(code__iexact=code)
        if not promo.is_active:
            request.session.pop('promo_code', None)
            request.session.pop('discount_percent', None)
            messages.error(request, 'This promo code is no longer active.')
            return HttpResponseRedirect(redirect_to)

        request.session['promo_code'] = promo.code
        request.session['discount_percent'] = promo.discount_percent
        messages.success(request, f'Promo code "{promo.code}" applied! You saved {promo.discount_percent}%')
        return HttpResponseRedirect(redirect_to)
    except PromoCode.DoesNotExist:
        request.session.pop('promo_code', None)
        request.session.pop('discount_percent', None)
        messages.error(request, 'Invalid promo code.')
        return HttpResponseRedirect(redirect_to)
