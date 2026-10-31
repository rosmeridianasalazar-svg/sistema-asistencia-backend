from django.db import models

class Roles(models.Model):
    id_rol = models.AutoField(primary_key=True)
    nombre = models.CharField(unique=True, max_length=50)
    descripcion = models.CharField(max_length=150, blank=True, null=True)
    estado = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'roles'
