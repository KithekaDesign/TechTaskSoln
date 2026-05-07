from rest_framework.routers import DefaultRouter
from .views import FraudFlagViewSet

router = DefaultRouter()
router.register(r'fraud', FraudFlagViewSet)

urlpatterns = router.urls
