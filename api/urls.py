from rest_framework import routers

from .views import UserViewSet, StudioViewSet, ReservationViewSet

app_name = 'api'

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'studios', StudioViewSet)
router.register(r'reservations', ReservationViewSet)

urlpatterns = router.urls
