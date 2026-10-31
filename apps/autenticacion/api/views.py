from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.permissions import AllowAny


from apps.autenticacion.api.serializers import LoginSerializer


class LoginAPIView(TokenObtainPairView):

    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    authentication_classes = []


class RefreshTokenAPIView(TokenRefreshView):

    permission_classes = [AllowAny]
    authentication_classes = []