from django.db import transaction, IntegrityError

from rest_framework import generics
from rest_framework.exceptions import APIException
from rest_framework.permissions import SAFE_METHODS

from apps.usuarios.api.serializers import (
    UsuarioCreateSerializer,
    UsuarioSerializer,
    UsuarioUpdateSerializer,
)

from apps.usuarios.selectors.usuario_selectors import obtener_usuarios

from apps.autenticacion.permissions import (
    EsAdministrador,
    EsAdministradorOPropietario,
)


class ConflictoEliminacion(APIException):
    status_code = 409
    default_detail = (
        "No se puede eliminar el usuario porque existe una "
        "relación que impide su eliminación."
    )
    default_code = 'conflicto_eliminacion'


class UsuarioListCreateAPIView(generics.ListCreateAPIView):

    permission_classes = [EsAdministrador]

    def get_queryset(self):
        return obtener_usuarios()

    def get_serializer_class(self):

        if self.request.method == 'POST':
            return UsuarioCreateSerializer

        return UsuarioSerializer


class UsuarioDetailAPIView(generics.RetrieveUpdateDestroyAPIView):

    lookup_field = 'id_usuario'

    def get_queryset(self):
        return obtener_usuarios()

    def get_permissions(self):

        if self.request.method in SAFE_METHODS:
            return [EsAdministradorOPropietario()]

        return [EsAdministrador()]

    def get_serializer_class(self):

        if self.request.method in ['PUT', 'PATCH']:
            return UsuarioUpdateSerializer

        return UsuarioSerializer

    def perform_destroy(self, instance):

        try:
            with transaction.atomic():
                instance.delete()

        except IntegrityError:
            raise ConflictoEliminacion()