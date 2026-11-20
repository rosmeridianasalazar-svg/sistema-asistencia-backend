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
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

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

class CumpleanosUsuariosAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        usuarios = obtener_usuarios().filter(
            estado=True,
            fecha_nacimiento__isnull=False
        )
        datos = [
            {
                'id_usuario': u.id_usuario,
                'nombre': u.nombre,
                'apellido_paterno': u.apellido_paterno,
                'apellido_materno': u.apellido_materno,
                'fecha_nacimiento': u.fecha_nacimiento,
                'nombre_rol': u.id_rol.nombre if getattr(u, 'id_rol', None) else 'Colaborador',
            }
            for u in usuarios
        ]
        return Response(datos, status=status.HTTP_200_OK)