from django.contrib import admin
from django import forms
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.urls import reverse
from django.utils.html import format_html

from apps.usuarios.models import Usuarios


class UsuarioAdminForm(forms.ModelForm):

    password = forms.CharField(
        label="Nueva contraseña",
        required=True,
        min_length=8,
        widget=forms.PasswordInput(
            render_value=False,
            attrs={
                'placeholder': 'Ingrese una nueva contraseña'
            }
        )
    )

    class Meta:
        model = Usuarios
        fields = '__all__'

    def clean_password(self):
        password = self.cleaned_data.get('password')

        if not password:
            raise forms.ValidationError(
                "Debe ingresar una nueva contraseña."
            )

        validate_password(password, self.instance)

        return make_password(password)


@admin.register(Usuarios)
class UsuariosAdmin(admin.ModelAdmin):

    form = UsuarioAdminForm

    list_select_related = ('id_rol',)
    show_full_result_count = False

    list_display = (
        'id_usuario',
        'dni',
        'nombre',
        'apellido_paterno',
        'correo',
        'id_rol',
        'estado',
        'acciones',
    )

    search_fields = (
        'dni',
        'nombre',
        'apellido_paterno',
        'apellido_materno',
        'correo',
    )

    list_filter = ('estado', 'id_rol')
    ordering = ('id_usuario',)

    readonly_fields = ('id_usuario',)

    fieldsets = (
        ('Información personal', {
            'fields': (
                'id_usuario',
                'dni',
                'nombre',
                'apellido_paterno',
                'apellido_materno',
                'telefono',
                'fecha_nacimiento',
            )
        }),
        ('Acceso al sistema', {
            'fields': (
                'correo',
                'password',
                'id_rol',
                'estado',
            )
        }),
    )

    @admin.display(description="Acciones")
    def acciones(self, obj):

        url_editar = reverse(
            'admin:usuarios_usuarios_change',
            args=[obj.pk]
        )

        url_eliminar = reverse(
            'admin:usuarios_usuarios_delete',
            args=[obj.pk]
        )

        return format_html(
            '<a class="button" href="{}" title="Editar" '
            'aria-label="Editar">✏️</a>&nbsp;'
            '<a class="button" href="{}" title="Eliminar" '
            'aria-label="Eliminar">🗑️</a>',
            url_editar,
            url_eliminar,
        )

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser