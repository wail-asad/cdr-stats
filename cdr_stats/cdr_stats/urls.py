from django.urls import path, re_path, include
from django.conf.urls import handler404, handler500
from django.conf import settings
from cdr.urls import urlpatterns as urlpatterns_cdr
from realtime.urls import urlpatterns as urlpatterns_realtime
from cdr_alert.urls import urlpatterns as urlpatterns_cdr_alert
from user_profile.urls import urlpatterns as urlpatterns_user_profile
from frontend.urls import urlpatterns as urlpatterns_frontend
from voip_billing.urls import urlpatterns as urlpatterns_voip_billing
from frontend_notification.urls import urlpatterns as urlpatterns_frontend_notification
from mod_registration.urls import urlpatterns as urlpatterns_mod_registration
from apirest.urls import urlpatterns as urlpatterns_apirest
from django.contrib import admin
from django.views.i18n import JavaScriptCatalog
from django.views.static import serve
from django.views.i18n import JavaScriptCatalog
import debug_toolbar

admin.autodiscover()

js_info_dict = {
    'domain': 'djangojs',
    'packages': ('cdr', 'cdr_alert'),
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path('jsi18n/', JavaScriptCatalog.as_view(), js_info_dict),
    # path('admin_tools/', include('admin_tools.urls')),
]

# Serve static files in development
if settings.DEBUG:
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
        path(r'^%s/(?P<path>.*)$' % settings.MEDIA_URL.strip('/'), serve, {'document_root': settings.MEDIA_ROOT}),
        path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    ]

# Add other URL patterns
urlpatterns += urlpatterns_cdr
urlpatterns += urlpatterns_realtime
urlpatterns += urlpatterns_cdr_alert
urlpatterns += urlpatterns_user_profile
urlpatterns += urlpatterns_frontend
urlpatterns += urlpatterns_frontend_notification
urlpatterns += urlpatterns_voip_billing
urlpatterns += urlpatterns_mod_registration
urlpatterns += urlpatterns_apirest

# # Custom error handlers
# handler404 = 'cdr_stats.urls.custom_404_view'
# handler500 = 'cdr_stats.urls.custom_500_view'