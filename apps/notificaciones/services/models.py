from django.db import models
from apps.usuarios.models import Usuarios


class Notificaciones(models.Model):
    id_notificacion = models.AutoField(primary_key=True)
    tipo = models.CharField(max_length=50)
    mensaje = models.TextField()
    estado_notificacion = models.CharField(max_length=1, default='P')  # 'P' = Pendiente (Sin leer), 'L' = Leído
    usuarios_id_usuario = models.ForeignKey(
        Usuarios,
        models.DO_NOTHING,
        db_column='usuarios_id_usuario',
        related_name='notificaciones_usuario',
    )

    class Meta:
        managed = False
        db_table = 'notificaciones'