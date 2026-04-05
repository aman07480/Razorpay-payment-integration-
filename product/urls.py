from django.urls import path
from .views import AddToCartView, CartCheckoutView, CartView, ClearCartView, ProductListView ,CheckoutView,CreatePaymentView,PaymentCallbackView,PaymentSuccessView, RemoveFromCartView,UpdateCartView

urlpatterns = [
    path("product/",ProductListView.as_view(),name="product_list"),
    # path("checkout/<int:product_id>/",CheckoutView.as_view(),name="Checkout"),
    path("checkout/<int:product_id>/",CheckoutView.as_view(),name="Checkout"),
    path("create-payment/<int:product_id>/",CreatePaymentView.as_view(),name="create_payment"),
    path("payment-verify/",PaymentCallbackView.as_view(),name="payment_verify"),
    path("payment-success/", PaymentSuccessView.as_view(), name="payment_success"),
     path("cart/", CartView.as_view(), name="cart"),
    path("add-to-cart/<int:product_id>/", AddToCartView.as_view(), name="add_to_cart"),
    path("remove/<int:item_id>/", RemoveFromCartView.as_view(), name="remove_from_cart"),
    path("update-cart/<int:item_id>/<str:action>/", UpdateCartView.as_view(), name="update_cart"),
    path("cart-checkout/", CartCheckoutView.as_view(), name="cart_checkout"),
    path("clear-cart/", ClearCartView.as_view(), name="clear_cart"),

    
]
