from django.db import models


class Horario(models.Model):
    id_horario = models.AutoField(primary_key=True)
    nombre = models.CharField(unique=True, max_length=100)
    hora_entrada = models.TimeField()
    hora_salida = models.TimeField()
    tolerancia_min = models.SmallIntegerField()
    estado_horario = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'horario'
        
class AsignacionHorario(models.Model):
    id_asignacion = models.AutoField(primary_key=True)
    usuarios_id_usuario = models.ForeignKey('usuarios.Usuarios', models.DB_CASCADE, db_column='usuarios_id_usuario')
    horario_id_horario = models.ForeignKey(Horario, models.DO_NOTHING, db_column='horario_id_horario')
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(blank=True, null=True)
    estado_asignacion = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'asignacion_horario'

class AsignacionDias(models.Model):
    id_dias = models.AutoField(primary_key=True)
    asignacion_horario_id_asignacion = models.ForeignKey(AsignacionHorario, models.DB_CASCADE, db_column='asignacion_horario_id_asignacion')
    dia_semana = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'asignacion_dias'
        unique_together = (('asignacion_horario_id_asignacion', 'dia_semana'),)


