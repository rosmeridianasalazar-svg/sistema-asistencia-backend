from rest_framework import serializers
from apps.roles.models import Roles


class RolesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Roles
        fields = [
            "id_rol",
            "nombre",
            "descripcion",
            "estado",
        ]
        read_only_fields = ["id_rol"]