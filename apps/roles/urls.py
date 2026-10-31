from rest_framework.routers import DefaultRouter
from apps.roles.views import RolesViewSet

router = DefaultRouter()
router.register("roles", RolesViewSet, basename="roles")

urlpatterns = router.urls