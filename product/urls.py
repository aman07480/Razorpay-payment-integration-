from django.urls import path
from .views import ProductListView ,CheckoutView,CreatePaymentView,PaymentCallbackView

urlpatterns = [
    path("product/",ProductListView.as_view(),name="product_list"),
    # path("checkout/<int:product_id>/",CheckoutView.as_view(),name="Checkout"),
    path("checkout/<int:product_id>/",CheckoutView.as_view(),name="Checkout"),
    path("create-payment/<int:product_id>/",CreatePaymentView.as_view(),name="create_payment"),
    path("payment-verify/",PaymentCallbackView.as_view(),name="payment_verify"),
    
]
