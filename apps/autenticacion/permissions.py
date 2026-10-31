from rest_framework.permissions import BasePermission


class TieneRol(BasePermission):

    roles_permitidos = []

    def has_permission(self, request, view):

        usuario = request.user

        if not usuario or not usuario.is_authenticated:
            return False

        if not usuario.is_active:
            return False

        if not usuario.id_rol:
            return False

        return usuario.id_rol.nombre in self.roles_permitidos


class EsAdministrador(TieneRol):

    roles_permitidos = ['Administrador']


class EsEmpleado(TieneRol):

    roles_permitidos = ['Empleado']


class EsPracticante(TieneRol):

    roles_permitidos = ['Practicante']


class EsAdministradorOPropietario(BasePermission):

    def has_permission(self, request, view):

        usuario = request.user

        return bool(
            usuario
            and usuario.is_authenticated
            and usuario.is_active
        )

    def has_object_permission(self, request, view, obj):

        usuario = request.user

        return (
            usuario.id_rol.nombre == 'Administrador'
            or usuario.id_usuario == obj.id_usuario
        )