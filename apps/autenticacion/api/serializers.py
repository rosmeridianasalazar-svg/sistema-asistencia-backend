from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class LoginSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)

        usuario = self.user

        data['usuario'] = {
            'id_usuario': usuario.id_usuario,
            'correo': usuario.correo,
            'nombre': usuario.nombre,
            'apellido_paterno': usuario.apellido_paterno,
            'apellido_materno': usuario.apellido_materno,
            'id_rol': usuario.id_rol_id,
            'rol': usuario.id_rol.nombre,
        }

        return data