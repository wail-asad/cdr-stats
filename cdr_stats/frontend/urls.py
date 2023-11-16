from django.urls import path, re_path
from frontend import views

urlpatterns = [
    path('', views.index, name='index'),
    path('index/', views.index, name='index'),
    path('diagnostic/', views.diagnostic, name='diagnostic'),
    path('login/', views.login_view, name='login_view'),
    path('logout/', views.logout_view, name='logout_view'),
    path('pleaselog/', views.pleaselog, name='pleaselog'),
    # ... other URL patterns ...
]