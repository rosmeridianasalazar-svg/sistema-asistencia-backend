from django.urls import path

from apps.usuarios.api.views import (
    UsuarioListCreateAPIView,
    UsuarioDetailAPIView
)

urlpatterns = [
    path(
        '',
        UsuarioListCreateAPIView.as_view(),
        name='usuarios-list-create'
    ),

    path(
        '<int:id_usuario>/',
        UsuarioDetailAPIView.as_view(),
        name='usuarios-detail'
    ),
]