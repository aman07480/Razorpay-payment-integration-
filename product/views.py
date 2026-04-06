from django.shortcuts import render
from django.http import JsonResponse
from django.shortcuts import render,get_object_or_404,redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from product.models import CartItem, Product,Order
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import razorpay
from django.conf import settings

client=razorpay.Client(auth=(settings.RAZORPAY_KEY_ID,settings.RAZORPAY_KEY_SECRET))
class ProductListView(View):
    def get(self,request):
        products=Product.objects.all()
        return render (request,"product/product_list.html", {"products":products})

# class CheckoutView(LoginRequiredMixin, View):
#     def get(self, request, product_id):
#         product = get_object_or_404(Product, id=product_id)

#         context = {
#             "product_name": product.name,
#             "amount": product.price
#         }

#         return render(request, "product/checkout.html", context)

class CheckoutView(LoginRequiredMixin, View):
    def get(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)

        razorpay_order = client.order.create({
            "amount": int(product.price * 100),
            "currency": "INR",
            "payment_capture": "1"
        })

        context = {
            "product": product,
            "order_id": razorpay_order["id"],
            "razorpay_key": settings.RAZORPAY_KEY_ID
        }

        return render(request, "product/checkout.html", context)

@method_decorator(csrf_exempt,name='dispatch')
class CreatePaymentView(LoginRequiredMixin,View):
    def post(self,request,product_id):
        product=get_object_or_404(Product,id=product_id)
        order_data={
            "amount":int(product.price * 100),
            "currency":"INR",
            "payment_capture":"1",

        }
        razorpay_order=client.order.create(order_data)
        Order.objects.create(
            user=request.user,
            product=product,
            amount=product.price,
            razorpay_order_id=razorpay_order["id"],
        )
        return JsonResponse({
            "order_id":razorpay_order["id"],
            "razorpay_key_id":settings.RAZORPAY_KEY_ID,
            "product_name":product.name,
            "amount":order_data["amount"],
            "razorpay_callback_url":settings.RAZORPAY_CALLBACK_URL
        })
    
# class PaymentCallbackView(View): 1
#     def post(self,request):
#         if "razorpay_signature" in request.POST:
#             order_id=request.POST.get("razorpay_order_id")
#             payment_id=request.POST.get("razorpay_payment_id")
#             signature=request.POST.get("razorpay_signature")

#             order=get_object_or_404(Order,razorpay_order_id=order_id)

#             if client.utility.verify_payment_signature({
#                 'razorpay_order_id':order_id,
#                 'razorpay_payment_id':payment_id,
#                 'razorpay_signature':signature,
#             }):
 
#                order.razorpay_payment_id=payment_id
#                order.razorpay_signature=signature
#                order.is_paid=True
#                order.save()
#                return JsonResponse({"status":"success"})
#             else:
#                 order.is_paid=False 
#                 order.save()
#                 return JsonResponse({"status":"failed"})
#         else:
#             return JsonResponse({"status":"failed"})


from django.shortcuts import redirect

@method_decorator(csrf_exempt, name='dispatch')
class PaymentCallbackView(View):
    def post(self, request):
        if "razorpay_signature" in request.POST:
            order_id = request.POST.get("razorpay_order_id")
            payment_id = request.POST.get("razorpay_payment_id")
            signature = request.POST.get("razorpay_signature")

            order = get_object_or_404(Order, razorpay_order_id=order_id)

            try:
                client.utility.verify_payment_signature({
                    'razorpay_order_id': order_id,
                    'razorpay_payment_id': payment_id,
                    'razorpay_signature': signature,
                })

                order.razorpay_payment_id = payment_id
                order.razorpay_signature = signature
                order.is_paid = True
                order.save()

                return redirect("payment_success")   # ✅ important

            except:
                order.is_paid = False
                order.save()
                return redirect("product_list")
            
        return redirect("product_list")
    
    

    
# @method_decorator(csrf_exempt,name='dispatch')
class PaymentSuccessView(View):
    def get(self, request):
        return render(request, "product/success.html")
    

class AddToCartView(LoginRequiredMixin, View):
    def get(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)

        cart_item, created = CartItem.objects.get_or_create(
            user=request.user,
            product=product
        )

        if not created:
            cart_item.quantity += 1
            cart_item.save()

        return redirect("cart")


# Cart Page
class CartView(LoginRequiredMixin, View):
    def get(self, request):
        cart_items = CartItem.objects.filter(user=request.user)

        total = sum(item.product.price * item.quantity for item in cart_items)

        return render(request, "product/cart.html", {
            "cart_items": cart_items,
            "total": total
        })

class RemoveFromCartView(LoginRequiredMixin, View):
    def get(self, request, item_id):
        item = get_object_or_404(CartItem, id=item_id)
        item.delete()
        return redirect("cart")
    

class UpdateCartView(LoginRequiredMixin, View):
    def get(self, request, item_id, action):
        item = get_object_or_404(CartItem, id=item_id)

        if action == "increase":
            item.quantity += 1

        elif action == "decrease":
            item.quantity -= 1
            if item.quantity <= 0:
                item.delete()
                return redirect("cart")

        item.save()
        return redirect("cart")
    
class CartCheckoutView(LoginRequiredMixin, View):
    def get(self, request):
        cart_items = CartItem.objects.filter(user=request.user)

        total = sum(item.product.price * item.quantity for item in cart_items)

        context = {
            "product_name": "Cart Items",
            "amount": total
        }

        return render(request, "product/checkout.html", context)


class ClearCartView(LoginRequiredMixin, View):
    def get(self, request):
        CartItem.objects.filter(user=request.user).delete()
        return redirect("cart") 
    
class OrderHistoryView(LoginRequiredMixin, View):
    def get(self, request):
        orders = Order.objects.filter(user=request.user).order_by("-id")
        return render(request, "product/order_history.html", {"orders": orders})