from django.urls import path, include
from rest_framework import routers
from apirest.view_user import UserViewSet
from apirest.view_switch import SwitchViewSet
from apirest.view_voip_rate import VoIPRateList

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'switch', SwitchViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browseable API.
urlpatterns = [
    path('rest-api/voip-rate/', VoIPRateList.as_view(), name="voip_rate"),
    path('rest-api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
