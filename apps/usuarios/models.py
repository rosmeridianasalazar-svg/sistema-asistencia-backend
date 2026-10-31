from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager

# class Usuarios(models.Model):
#     id_usuario = models.AutoField(primary_key=True)
#     id_rol = models.ForeignKey('roles.Roles', models.DO_NOTHING, db_column='id_rol')
#     dni = models.CharField(unique=True, max_length=8)
#     nombre = models.CharField(max_length=50)
#     apellido_paterno = models.CharField(max_length=50)
#     apellido_materno = models.CharField(max_length=50, blank=True, null=True)
#     telefono = models.CharField(max_length=20, blank=True, null=True)
#     correo = models.CharField(unique=True, max_length=100)
#     password = models.CharField(max_length=128)
#     fecha_nacimiento = models.DateField(blank=True, null=True)
#     estado = models.BooleanField()

#     class Meta:
#         managed = False
#         db_table = 'usuarios'

class UsuarioManager(BaseUserManager):

    def create_user(self, correo, password=None, **extra_fields):
        if not correo:
            raise ValueError("El correo electrónico es obligatorio")
        if not password:
            raise ValueError("La contraseña es obligatoria")

        correo = self.normalize_email(correo)
        # si no se especifica el usuario se registra activo.
        extra_fields.setdefault('estado', True)
        usuario = self.model(correo=correo,**extra_fields)
        # django genera el hash de la contraseña.
        usuario.set_password(password)
        usuario.save(using=self._db) #guarda en la base de datos

        return usuario

class Usuarios(AbstractBaseUser):

    # identificador principal
    id_usuario = models.AutoField(primary_key=True)
    # relación con roles
    id_rol = models.ForeignKey('roles.Roles',models.DO_NOTHING,db_column='id_rol',related_name='usuarios')
    dni = models.CharField(unique=True, max_length=8)
    nombre = models.CharField(max_length=50)
    apellido_paterno = models.CharField(max_length=50)
    apellido_materno = models.CharField(max_length=50,blank=True,null=True)
    telefono = models.CharField(max_length=20,blank=True,null=True)
    # credenciales
    correo = models.CharField(unique=True,max_length=100)

    # la contraseña se hereda de AbstractBaseUser.
    # no necesitamos declararla nuevamente.

    fecha_nacimiento = models.DateField(blank=True,null=True)
    estado = models.BooleanField(default=True)

    # AbstractBaseUser incluye last_login,
    # pero esa columna no existe en nuestra tabla.
    last_login = None

    # administrador personalizado
    objects = UsuarioManager()

    # Configuración de autenticación
    USERNAME_FIELD = 'correo'

    REQUIRED_FIELDS = [
        'dni',
        'nombre',
        'apellido_paterno'
    ]

    # relacionamos el estado existente con Django
    # Estado de la cuenta
    @property
    def is_active(self):
        return self.estado

    @is_active.setter
    def is_active(self, value):
        self.estado = value

    # Acceso al panel de administración
    @property
    def is_staff(self):
        return (
            self.is_active
            and self.id_rol.nombre == 'Administrador'
        )

    # Permisos de superusuario
    @property
    def is_superuser(self):
        return (
            self.is_active
            and self.id_rol.nombre == 'Administrador'
        )

    # Comprobación de permisos
    def has_perm(self, perm, obj=None):
        return self.is_active and self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_active and self.is_superuser

    def get_full_name(self):
        return (
            f"{self.nombre} "
            f"{self.apellido_paterno} "
            f"{self.apellido_materno or ''}"
        ).strip()

    def __str__(self):
        return self.correo

    class Meta:
        managed = False
        db_table = 'usuarios'



class Huellas(models.Model):
    id_huella = models.AutoField(primary_key=True)
    usuarios_id_usuario = models.ForeignKey(Usuarios, models.DO_NOTHING, db_column='usuarios_id_usuario',related_name='huellas')
    huella_id_sensor = models.SmallIntegerField(unique=True)
    mano = models.CharField(max_length=10)
    dedo = models.CharField(max_length=15)
    estado_huella = models.BooleanField()
    fecha_registro = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'huellas'
        unique_together = (('usuarios_id_usuario', 'mano', 'dedo'),)
