from apps.usuarios.models import Usuarios


def obtener_usuarios():
    return Usuarios.objects.select_related(
        'id_rol'
    ).order_by('id_usuario')


def obtener_usuario_por_id(id_usuario):
    return Usuarios.objects.select_related(
        'id_rol'
    ).filter(
        id_usuario=id_usuario
    ).first()