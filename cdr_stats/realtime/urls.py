from django.urls import path, re_path
from realtime import views

urlpatterns = [
    path('concurrent_calls/', views.cdr_concurrent_calls),
    path('realtime/', views.cdr_realtime),
    # Uncomment and update the following line if you have a corresponding view function
    # path('get_realtime_json/', views.get_realtime_json),
]
