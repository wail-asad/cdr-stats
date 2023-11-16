from django.urls import path, re_path
from voip_billing import views

urlpatterns = [
    path('rates/', views.voip_rates, name='voip_rates'),
    path('export_rate/', views.export_rate, name='export_rate'),
    path('simulator/', views.simulator, name='simulator'),
    path('billing_report/', views.billing_report, name='billing_report'),
    # ... other URL patterns ...
]
