from datetime import date
from django.db import transaction
from django.db.models import Q
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.horarios.models import Horario, AsignacionHorario, AsignacionDias
from apps.horarios.api.serializers import HorarioSerializer, AsignacionHorarioSerializer
from apps.usuarios.models import Usuarios


def es_administrador(user):
    rol = getattr(user, 'id_rol', None)
    nombre_rol = getattr(rol, 'nombre', '') if rol else ''
    return nombre_rol.strip().lower() == 'administrador'


class HorarioListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        horarios = Horario.objects.all().order_by('hora_entrada', 'nombre')
        serializer = HorarioSerializer(horarios, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        if not es_administrador(request.user):
            return Response({'detail': 'No tienes permisos para crear horarios.'}, status=status.HTTP_403_FORBIDDEN)

        data = request.data.copy()
        data.setdefault('estado_horario', True)
        data.setdefault('tolerancia_min', 10)

        serializer = HorarioSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HorarioDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, id_horario):
        if not es_administrador(request.user):
            return Response({'detail': 'No tienes permisos para editar horarios.'}, status=status.HTTP_403_FORBIDDEN)

        horario = Horario.objects.filter(pk=id_horario).first()
        if not horario:
            return Response({'detail': 'Horario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = HorarioSerializer(horario, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id_horario):
        if not es_administrador(request.user):
            return Response({'detail': 'No tienes permisos para eliminar horarios.'}, status=status.HTTP_403_FORBIDDEN)

        horario = Horario.objects.filter(pk=id_horario).first()
        if not horario:
            return Response({'detail': 'Horario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        if AsignacionHorario.objects.filter(horario_id_horario=horario, estado_asignacion=True).exists():
            return Response(
                {'detail': 'No puedes eliminar este turno porque está asignado a colaboradores activos.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        horario.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AsignacionHorarioListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        asignaciones = (
            AsignacionHorario.objects.select_related('usuarios_id_usuario', 'usuarios_id_usuario__id_rol', 'horario_id_horario')
            .filter(estado_asignacion=True, usuarios_id_usuario__estado=True)
            .order_by('horario_id_horario__hora_entrada', 'usuarios_id_usuario__nombre')
        )
        serializer = AsignacionHorarioSerializer(asignaciones, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        if not es_administrador(request.user):
            return Response({'detail': 'Solo el administrador puede asignar horarios.'}, status=status.HTTP_403_FORBIDDEN)

        usuario_id = request.data.get('usuarios_id_usuario')
        fecha_inicio = request.data.get('fecha_inicio') or str(date.today())
        fecha_fin = request.data.get('fecha_fin') or None

        # Soporta múltiples bloques en una sola petición o un bloque único
        bloques = request.data.get('bloques')
        if not bloques and request.data.get('horario_id_horario'):
            bloques = [{
                'horario_id_horario': request.data.get('horario_id_horario'),
                'dias': request.data.get('dias', []),
            }]

        if not usuario_id or not bloques:
            return Response(
                {'detail': 'Debes seleccionar un colaborador y al menos un bloque horario con sus días.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        usuario = Usuarios.objects.filter(pk=usuario_id, estado=True).first()
        if not usuario:
            return Response({'detail': 'Colaborador no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        nombres_dias = {1: 'Lunes', 2: 'Martes', 3: 'Miércoles', 4: 'Jueves', 5: 'Viernes', 6: 'Sábado', 7: 'Domingo'}
        dias_nuevos_totales = set()
        bloques_validados = []

        for idx, b in enumerate(bloques, start=1):
            h_id = b.get('horario_id_horario')
            dias_raw = b.get('dias', [])
            if not h_id or not dias_raw:
                return Response(
                    {'detail': f'Completa el turno y los días en el bloque #{idx}.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            horario = Horario.objects.filter(pk=h_id, estado_horario=True).first()
            if not horario:
                return Response({'detail': f'Turno no válido en el bloque #{idx}.'}, status=status.HTTP_404_NOT_FOUND)

            dias_limpios = sorted({int(d) for d in dias_raw if 1 <= int(d) <= 7})
            repetidos_internos = dias_nuevos_totales.intersection(dias_limpios)
            if repetidos_internos:
                lista_txt = ', '.join(nombres_dias[d] for d in sorted(repetidos_internos))
                return Response(
                    {'detail': f'Estás repitiendo días entre tus bloques: {lista_txt}.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            dias_nuevos_totales.update(dias_limpios)
            bloques_validados.append((horario, dias_limpios))

        # Validar contra asignaciones ya existentes en BD
        asignaciones_previas = AsignacionHorario.objects.filter(
            usuarios_id_usuario=usuario,
            estado_asignacion=True,
        ).filter(Q(fecha_fin__isnull=True) | Q(fecha_fin__gte=fecha_inicio))

        dias_ocupados = set(
            AsignacionDias.objects.filter(
                asignacion_horario_id_asignacion__in=asignaciones_previas,
                dia_semana__in=dias_nuevos_totales,
            ).values_list('dia_semana', flat=True)
        )

        if dias_ocupados:
            lista_txt = ', '.join(nombres_dias[d] for d in sorted(dias_ocupados))
            return Response(
                {'detail': f'Este colaborador ya tiene un horario asignado para: {lista_txt}.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        creadas = []
        with transaction.atomic():
            for horario, dias_limpios in bloques_validados:
                asignacion = AsignacionHorario.objects.create(
                    usuarios_id_usuario=usuario,
                    horario_id_horario=horario,
                    fecha_inicio=fecha_inicio,
                    fecha_fin=fecha_fin,
                    estado_asignacion=True,
                )
                AsignacionDias.objects.bulk_create([
                    AsignacionDias(asignacion_horario_id_asignacion=asignacion, dia_semana=d)
                    for d in dias_limpios
                ])
                creadas.append(asignacion)

        serializer = AsignacionHorarioSerializer(creadas, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AsignacionHorarioDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, id_asignacion):
        if not es_administrador(request.user):
            return Response({'detail': 'Solo el administrador puede eliminar asignaciones.'}, status=status.HTTP_403_FORBIDDEN)

        asignacion = AsignacionHorario.objects.filter(pk=id_asignacion).first()
        if not asignacion:
            return Response({'detail': 'Asignación no encontrada.'}, status=status.HTTP_404_NOT_FOUND)

        with transaction.atomic():
            AsignacionDias.objects.filter(asignacion_horario_id_asignacion=asignacion).delete()
            asignacion.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)