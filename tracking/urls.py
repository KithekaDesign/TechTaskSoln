from rest_framework.routers import DefaultRouter
from .views import TimeLogViewSet

router = DefaultRouter()
router.register(r'timelogs', TimeLogViewSet)

urlpatterns = router.urls
