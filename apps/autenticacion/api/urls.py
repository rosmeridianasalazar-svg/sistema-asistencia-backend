from django.urls import path

from apps.autenticacion.api.views import (
    LoginAPIView,
    RefreshTokenAPIView,

    #conectamos
    SolicitarRecuperacionAPIView,
    ConfirmarRecuperacionAPIView,
)

urlpatterns = [
    path(
        'login/',
        LoginAPIView.as_view(),
        name='login'
    ),

    path(
        'refresh/',
        RefreshTokenAPIView.as_view(),
        name='token-refresh'
    ),

    #-----
    path('recuperar-password/', SolicitarRecuperacionAPIView.as_view(), name='recuperar-password'),
    path('restablecer-password/', ConfirmarRecuperacionAPIView.as_view(), name='restablecer-password'),
]