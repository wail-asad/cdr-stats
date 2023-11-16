from django.urls import path, re_path
from cdr_alert import views

urlpatterns = [
    path('alert/', views.alarm_list, name='alarm_list'),
    path('alert/add/', views.alarm_add, name='alarm_add'),
    re_path(r'^alert/del/(?P<alarm_id>.+)/$', views.alarm_del, name='alarm_del'),
    re_path(r'^alert/test/(?P<test_id>.+)/$', views.alarm_test, name='alarm_test'),
    re_path(r'^alert/(?P<alarm_id>.+)/$', views.alarm_change, name='alarm_change'),

    path('trust_control/', views.trust_control, name='trust_control'),
    path('alert_report/', views.alert_report, name='alert_report'),
]
