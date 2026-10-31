from django.db import transaction

from apps.usuarios.models import Usuarios


@transaction.atomic
def registrar_usuario(datos):
    return Usuarios.objects.create_user(**datos)