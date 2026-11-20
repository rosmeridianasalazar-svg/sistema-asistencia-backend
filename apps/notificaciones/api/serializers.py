from rest_framework import serializers
from apps.notificaciones.services.models import Notificaciones


class NotificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notificaciones
        fields = [
            'id_notificacion',
            'tipo',
            'mensaje',
            'estado_notificacion',
            'usuarios_id_usuario',
        ]


class CrearNotificacionSerializer(serializers.Serializer):
    destinatario = serializers.CharField()
    mensaje = serializers.CharField()