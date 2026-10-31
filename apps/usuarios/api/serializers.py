from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password

from apps.usuarios.models import Usuarios
from apps.roles.models import Roles
from apps.usuarios.services.usuario_services import registrar_usuario


class UsuarioCreateSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True,
        min_length=8,
        validators=[validate_password]
    )

    id_rol = serializers.PrimaryKeyRelatedField(
        queryset=Roles.objects.filter(estado=True)
    )

    class Meta:
        model = Usuarios
        fields = [
            'id_usuario',
            'id_rol',
            'dni',
            'nombre',
            'apellido_paterno',
            'apellido_materno',
            'telefono',
            'correo',
            'password',
            'fecha_nacimiento',
        ]
        read_only_fields = ['id_usuario']

    def validate_dni(self, value):
        value = value.strip()

        if not value.isdigit() or len(value) != 8:
            raise serializers.ValidationError(
                "El DNI debe contener exactamente 8 dígitos."
            )

        return value

    def validate_correo(self, value):
        return value.strip().lower()

    def create(self, validated_data):
        return registrar_usuario(validated_data)


class UsuarioUpdateSerializer(serializers.ModelSerializer):

    id_rol = serializers.PrimaryKeyRelatedField(
        queryset=Roles.objects.filter(estado=True)
    )

    class Meta:
        model = Usuarios
        fields = [
            'id_usuario',
            'id_rol',
            'dni',
            'nombre',
            'apellido_paterno',
            'apellido_materno',
            'telefono',
            'correo',
            'fecha_nacimiento',
            'estado',
        ]
        read_only_fields = ['id_usuario']

    def validate_dni(self, value):
        value = value.strip()

        if len(value) != 8 or not value.isdigit():
            raise serializers.ValidationError(
                "El DNI debe contener exactamente 8 dígitos."
            )

        return value

    def validate_correo(self, value):
        return value.strip().lower()


class UsuarioSerializer(serializers.ModelSerializer):

    class Meta:
        model = Usuarios
        fields = [
            'id_usuario',
            'id_rol',
            'dni',
            'nombre',
            'apellido_paterno',
            'apellido_materno',
            'telefono',
            'correo',
            'fecha_nacimiento',
            'estado',
        ]
        read_only_fields = fields