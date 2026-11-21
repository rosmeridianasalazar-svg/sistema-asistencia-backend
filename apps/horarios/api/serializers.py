from rest_framework import serializers
from apps.horarios.models import Horario, AsignacionHorario, AsignacionDias


class HorarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Horario
        fields = [
            'id_horario',
            'nombre',
            'hora_entrada',
            'hora_salida',
            'tolerancia_min',
            'estado_horario',
        ]


class AsignacionHorarioSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.SerializerMethodField()
    usuario_rol = serializers.SerializerMethodField()
    horario_detalle = HorarioSerializer(source='horario_id_horario', read_only=True)
    dias = serializers.SerializerMethodField()

    class Meta:
        model = AsignacionHorario
        fields = [
            'id_asignacion',
            'usuarios_id_usuario',
            'usuario_nombre',
            'usuario_rol',
            'horario_id_horario',
            'horario_detalle',
            'fecha_inicio',
            'fecha_fin',
            'estado_asignacion',
            'dias',
        ]

    def get_usuario_nombre(self, obj):
        u = obj.usuarios_id_usuario
        return ' '.join(filter(None, [u.nombre, u.apellido_paterno, u.apellido_materno]))

    def get_usuario_rol(self, obj):
        u = obj.usuarios_id_usuario
        return u.id_rol.nombre if getattr(u, 'id_rol', None) else 'Colaborador'

    def get_dias(self, obj):
        return list(
            AsignacionDias.objects.filter(asignacion_horario_id_asignacion=obj)
            .order_by('dia_semana')
            .values_list('dia_semana', flat=True)
        )