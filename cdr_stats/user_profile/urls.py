from django.urls import path, re_path
from user_profile import views

urlpatterns = [
    path('user_detail_change/', views.customer_detail_change, name='customer_detail_change'),
    # Use re_path if you need regular expressions for other URLs
]
