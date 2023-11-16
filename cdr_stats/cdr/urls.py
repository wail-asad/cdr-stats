from django.urls import path, re_path
from cdr import views  # Import your views here

urlpatterns = [
    path('cdr_view/', views.cdr_view),
    path('cdr_export_csv/', views.cdr_export_to_csv),
    re_path(r'^cdr_detail/(?P<cdr_id>\w+)/$', views.cdr_detail),
    path('dashboard/', views.cdr_dashboard),
    path('daily_comparison/', views.cdr_daily_comparison),
    path('overview/', views.cdr_overview),
    path('mail_report/', views.mail_report),
    path('country_report/', views.cdr_country_report),
    path('world_map/', views.world_map_view),
]
