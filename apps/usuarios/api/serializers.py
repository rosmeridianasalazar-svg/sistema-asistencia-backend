from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
#validaciones
from django.db.models import Q
from rest_framework.validators import UniqueValidator
from django.core.validators import EmailValidator

from apps.usuarios.models import Usuarios
from apps.roles.models import Roles
from apps.usuarios.services.usuario_services import registrar_usuario

#validador de unicidad conjunta para los campos dni, telefono y correo

class ValidacionUnicaConjuntaMixin:
    CAMPOS_UNICOS = ('dni', 'telefono', 'correo')

    def get_fields(self):
        fields = super().get_fields()

        for campo in self.CAMPOS_UNICOS:
            if campo in fields:
                fields[campo].validators = [
                    v for v in fields[campo].validators
                    if not isinstance(v, (UniqueValidator, EmailValidator))
                ]

        return fields

    def validar_unicidad_conjunta(self, attrs):
        filtros = Q()
        valores = {}

        for campo in self.CAMPOS_UNICOS:
            valor = attrs.get(campo)
            if valor not in (None, ''):
                valores[campo] = valor
                filtros |= Q(**{campo: valor})

        if not filtros:
            return {}

        coincidencias = Usuarios.objects.filter(filtros)

        # Excluimos al usuario actual en actualizaciones (PATCH/PUT)
        if self.instance:
            coincidencias = coincidencias.exclude(pk=self.instance.pk)

        registros = coincidencias.values_list(*self.CAMPOS_UNICOS)
        errores = {}

        for fila in registros:
            datos_db = dict(zip(self.CAMPOS_UNICOS, fila))
            for campo, valor in valores.items():
                if valor == datos_db[campo]:
                    errores[campo] = [f'Este {campo} ya está registrado.']

        return errores

#validaciones usuario unitario
class UsuarioValidacionesMixin:
    DOMINIOS_PERMITIDOS = ('gmail.com', 'hotmail.com', 'outlook.com')

    def _validar_dni(self, attrs, errores):
        if 'dni' not in attrs or attrs['dni'] in (None, ''):
            return

        dni = str(attrs['dni']).strip()
        attrs['dni'] = dni

        if len(dni) != 8 or not dni.isdigit():
            errores.setdefault('dni', []).append(
                'El DNI debe contener exactamente 8 dígitos.'
            )

    def _validar_telefono(self, attrs, errores):
        if 'telefono' not in attrs or attrs['telefono'] in (None, ''):
            return

        telefono = str(attrs['telefono']).strip()
        attrs['telefono'] = telefono

        if len(telefono) != 9 or not telefono.isdigit():
            errores.setdefault('telefono', []).append(
                'El teléfono debe contener exactamente 9 dígitos.'
            )

    def _validar_correo(self, attrs, errores):
        if 'correo' not in attrs or attrs['correo'] in (None, ''):
            return

        correo = str(attrs['correo']).strip().lower()
        attrs['correo'] = correo

        if '@' not in correo:
            errores.setdefault('correo', []).append(
                "El correo debe contener un '@'."
            )
            return

        usuario, dominio = correo.split('@', 1)

        if not usuario:
            errores.setdefault('correo', []).append(
                "Ingresa un nombre antes del '@'."
            )
        elif not dominio.endswith('.com') or dominio not in self.DOMINIOS_PERMITIDOS:
            errores.setdefault('correo', []).append(
                'Usa un correo válido con dominio gmail.com, hotmail.com o outlook.com.'
            )

    def _validar_password(self, attrs, errores):
        password = attrs.get('password')
        if not password:
            return

        try:
            validate_password(password, self.instance)
        except Exception as e:
            errores.setdefault('password', []).extend(list(e.messages))

    def validate(self, attrs):
        attrs = super().validate(attrs)
        errores = {}

        #validaciones de formato (normalizan attrs antes de consultar la BD)
        self._validar_dni(attrs, errores)
        self._validar_telefono(attrs, errores)
        self._validar_correo(attrs, errores)
        self._validar_password(attrs, errores)

        #validación de duplicados en BD (usa los attrs ya limpios y en minúsculas)
        if hasattr(self, 'validar_unicidad_conjunta'):
            errores_duplicados = self.validar_unicidad_conjunta(attrs)
            for campo, mensajes in errores_duplicados.items():
                errores.setdefault(campo, []).extend(mensajes)

        if errores:
            raise serializers.ValidationError(errores)

        return attrs

class UsuarioCreateSerializer(UsuarioValidacionesMixin, ValidacionUnicaConjuntaMixin, serializers.ModelSerializer):
    correo = serializers.CharField(max_length=100)
    password = serializers.CharField(
        write_only=True,
        min_length=8,
    )

    id_rol = serializers.PrimaryKeyRelatedField(
        queryset=Roles.objects.filter(estado=True).only('id_rol')
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
    def create(self, validated_data):
        return registrar_usuario(validated_data)


class UsuarioUpdateSerializer(UsuarioValidacionesMixin, ValidacionUnicaConjuntaMixin, serializers.ModelSerializer):
    correo = serializers.CharField(max_length=100)
    password = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        min_length=8
    )

    id_rol = serializers.PrimaryKeyRelatedField(
        queryset=Roles.objects.filter(estado=True).only('id_rol'))

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
            'estado',
        ]
        read_only_fields = ['id_usuario']
        
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)

        #actualizar los demás campos del usuario
        for campo, valor in validated_data.items():
            setattr(instance, campo, valor)

        #cambiar la contraseña unicamente si se proporcionó una
        if password:
            instance.set_password(password)

        instance.save()

        return instance

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