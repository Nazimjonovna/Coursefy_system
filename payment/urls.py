from django.urls import path
from payment.views import PaymentCourseView, PaymentTestView, TestingPayment, PaymentHistoryAdminList, PaymentHistoryPupil
from payment.merchant_api import MerchantAPIView


urlpatterns = [
    path('', MerchantAPIView.as_view()),
    path('user/payment/history/', PaymentHistoryPupil.as_view()),
    path('admin/payment/history/', PaymentHistoryAdminList.as_view()),
    path('sell/course/', PaymentCourseView.as_view()),
    path('sell/test/', PaymentTestView.as_view()),
    path('testing/payment/', TestingPayment.as_view()),
    # path('merchant-api/', MerchantAPIVi.ew.as_view()),
]
