from django.db import models

class Asistencias(models.Model):
    id_asistencia = models.BigAutoField(primary_key=True)
    fecha_hora_evento = models.DateTimeField()
    fecha_hora_recepcion = models.DateTimeField()
    tipo_evento = models.CharField(max_length=10)
    confianza = models.SmallIntegerField()
    estado_asistencia = models.CharField(max_length=20)
    huellas_id_huella = models.ForeignKey('usuarios.Huellas', models.DB_CASCADE, db_column='huellas_id_huella')

    class Meta:
        managed = False
        db_table = 'asistencias'

class Sustentaciones(models.Model):
    id_sustentacion = models.AutoField(primary_key=True)
    fecha_sustentacion = models.DateField()
    titulo = models.CharField(max_length=150)
    descripcion = models.CharField(max_length=500)
    estado_sustentacion = models.CharField(max_length=20)
    usuarios_id_usuario = models.ForeignKey('usuarios.Usuarios', models.DB_CASCADE, db_column='usuarios_id_usuario')
    asistencias_id_asistencia = models.ForeignKey(Asistencias, models.DB_SET_NULL, db_column='asistencias_id_asistencia', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sustentaciones'

class Notificaciones(models.Model):
    id_notificacion = models.AutoField(primary_key=True)
    tipo = models.CharField(max_length=40)
    mensaje = models.CharField(max_length=255)
    estado_notificacion = models.CharField(max_length=1)
    usuarios_id_usuario = models.ForeignKey('usuarios.Usuarios', models.DB_CASCADE, db_column='usuarios_id_usuario')

    class Meta:
        managed = False
        db_table = 'notificaciones'

