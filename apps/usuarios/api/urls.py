from django.urls import path

from apps.usuarios.api.views import (
    UsuarioListCreateAPIView,
    UsuarioDetailAPIView,
    CumpleanosUsuariosAPIView,
)

urlpatterns = [
    path(
        '',
        UsuarioListCreateAPIView.as_view(),
        name='usuarios-list-create'
    ),

    path(
        'cumpleanos/',
        CumpleanosUsuariosAPIView.as_view(),
        name='usuarios-cumpleanos'
    ),

    path(
        '<int:id_usuario>/',
        UsuarioDetailAPIView.as_view(),
        name='usuarios-detail'
    ),
]