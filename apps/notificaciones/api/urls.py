from django.urls import path
from apps.notificaciones.api.views import (
    NotificacionListCreateAPIView,
    MarcarNotificacionLeidaAPIView,
    EliminarNotificacionAPIView,
    DestinatariosListAPIView,
    EliminarTodasNotificacionesAPIView,
)

urlpatterns = [
    path('', NotificacionListCreateAPIView.as_view(), name='notificaciones-list-create'),
    path('<int:id_notificacion>/leer/', MarcarNotificacionLeidaAPIView.as_view(), name='notificacion-leer'),
    path('<int:id_notificacion>/eliminar/', EliminarNotificacionAPIView.as_view(), name='notificacion-eliminar'),
    path('destinatarios/', DestinatariosListAPIView.as_view(), name='notificaciones-destinatarios'),
    path('eliminar-todas/', EliminarTodasNotificacionesAPIView.as_view(), name='notificaciones-eliminar-todas'),
]