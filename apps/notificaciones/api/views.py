from django.db import transaction
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.notificaciones.services.models import Notificaciones
from apps.notificaciones.api.serializers import (
    NotificacionSerializer,
    CrearNotificacionSerializer,
)
from apps.usuarios.models import Usuarios
from apps.usuarios.selectors.usuario_selectors import obtener_usuarios


class NotificacionListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notificaciones = Notificaciones.objects.filter(
            usuarios_id_usuario=request.user
        ).order_by('-id_notificacion')

        serializer = NotificacionSerializer(notificaciones, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CrearNotificacionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        destinatario = serializer.validated_data['destinatario'].strip()
        mensaje = serializer.validated_data['mensaje'].strip()

        if not mensaje:
            return Response(
                {'detail': 'El mensaje no puede estar vacío.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        remitente = request.user.get_full_name() or request.user.correo
        mensaje_recibido = f"[De: {remitente}]\n{mensaje}"

        with transaction.atomic():
            if destinatario.upper() == 'TODOS':
                # Excluimos al usuario que envía el anuncio para que no le llegue como recibido
                destinatarios = obtener_usuarios().exclude(pk=request.user.pk)

                nuevas_recibidas = [
                    Notificaciones(
                        tipo='ANUNCIO',
                        mensaje=mensaje_recibido,
                        estado_notificacion='P',
                        usuarios_id_usuario=u,
                    )
                    for u in destinatarios
                ]
                Notificaciones.objects.bulk_create(nuevas_recibidas)

                # Guardamos registro en la bandeja de ENVIADOS ('E') del emisor
                Notificaciones.objects.create(
                    tipo='ANUNCIO',
                    mensaje=f"[Para: Todos los usuarios]\n{mensaje}",
                    estado_notificacion='E',
                    usuarios_id_usuario=request.user,
                )

                return Response(
                    {'detail': f'Anuncio enviado a {len(nuevas_recibidas)} usuarios.'},
                    status=status.HTTP_201_CREATED,
                )

            usuario_destino = Usuarios.objects.filter(pk=destinatario).first()
            if not usuario_destino:
                return Response(
                    {'detail': 'El usuario destinatario no existe.'},
                    status=status.HTTP_404_NOT_FOUND,
                )

            Notificaciones.objects.create(
                tipo='MENSAJE',
                mensaje=mensaje_recibido,
                estado_notificacion='P',
                usuarios_id_usuario=usuario_destino,
            )

            # Guardamos copia en ENVIADOS ('E') del emisor
            Notificaciones.objects.create(
                tipo='MENSAJE',
                mensaje=f"[Para: {usuario_destino.get_full_name()}]\n{mensaje}",
                estado_notificacion='E',
                usuarios_id_usuario=request.user,
            )

            return Response(
                {'detail': f'Mensaje enviado a {usuario_destino.get_full_name()}.'},
                status=status.HTTP_201_CREATED,
            )


class MarcarNotificacionLeidaAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, id_notificacion):
        notificacion = Notificaciones.objects.filter(
            pk=id_notificacion,
            usuarios_id_usuario=request.user,
        ).first()

        if not notificacion:
            return Response(
                {'detail': 'Notificación no encontrada.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        if notificacion.estado_notificacion == 'P':
            notificacion.estado_notificacion = 'L'
            notificacion.save(update_fields=['estado_notificacion'])

        return Response(
            NotificacionSerializer(notificacion).data,
            status=status.HTTP_200_OK,
        )


class EliminarNotificacionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, id_notificacion):
        notificacion = Notificaciones.objects.filter(
            pk=id_notificacion,
            usuarios_id_usuario=request.user,
        ).first()

        if not notificacion:
            return Response(
                {'detail': 'Notificación no encontrada.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        notificacion.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DestinatariosListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        usuarios = (
            obtener_usuarios()
            .exclude(pk=request.user.pk)
            .order_by('nombre', 'apellido_paterno')
        )
        datos = [
            {
                'id_usuario': u.id_usuario,
                'nombre_completo': u.get_full_name(),
                'dni': getattr(u, 'dni', '') or '',
                'correo': u.correo,
            }
            for u in usuarios
        ]
        return Response(datos, status=status.HTTP_200_OK)

class EliminarTodasNotificacionesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        bandeja = request.query_params.get('bandeja', 'RECIBIDOS').upper()
        queryset = Notificaciones.objects.filter(usuarios_id_usuario=request.user)

        if bandeja == 'ENVIADOS':
            queryset = queryset.filter(estado_notificacion='E')
        else:
            queryset = queryset.exclude(estado_notificacion='E')

        eliminadas, _ = queryset.delete()
        return Response(
            {'detail': f'Se eliminaron {eliminadas} notificaciones.'},
            status=status.HTTP_200_OK,
        )