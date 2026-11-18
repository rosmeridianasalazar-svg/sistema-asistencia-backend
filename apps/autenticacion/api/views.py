# from rest_framework_simplejwt.views import TokenObtainPairView
# from rest_framework_simplejwt.views import TokenRefreshView
# from rest_framework.permissions import AllowAny


# from apps.autenticacion.api.serializers import LoginSerializer


# class LoginAPIView(TokenObtainPairView):

#     serializer_class = LoginSerializer
#     permission_classes = [AllowAny]
#     authentication_classes = []


# class RefreshTokenAPIView(TokenRefreshView):

#     permission_classes = [AllowAny]
#     authentication_classes = []

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import signing
from django.core.mail import send_mail
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.autenticacion.api.serializers import LoginSerializer

Usuario = get_user_model()
SALT_RECUPERACION = 'recuperar-password-nexos'


class LoginAPIView(TokenObtainPairView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    authentication_classes = []


class RefreshTokenAPIView(TokenRefreshView):
    permission_classes = [AllowAny]
    authentication_classes = []


class SolicitarRecuperacionAPIView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        correo = request.data.get('correo', '').strip().lower()
        if not correo:
            return Response(
                {'detail': 'Debes ingresar un correo electrónico.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        usuario = Usuario.objects.filter(correo__iexact=correo, estado=True).first()
        if not usuario:
            return Response(
                {'detail': 'No encontramos una cuenta activa con este correo.'},
                status=status.HTTP_404_NOT_FOUND
            )

        token = signing.dumps(
            {'id_usuario': usuario.pk, 'ph': usuario.password[:12]},
            salt=SALT_RECUPERACION
        )

        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')
        enlace = f"{frontend_url}/restablecer-password?token={token}"

        # Texto plano de respaldo 
        mensaje_texto = (
            f"Hola {usuario.nombre},\n\n"
            f"Solicitaste restablecer tu contraseña en Sistema Nexos.\n"
            f"Ingresa al siguiente enlace (válido por 15 minutos):\n{enlace}\n\n"
            f"Si no fuiste tú, ignora este correo."
        )

        # Diseño visual en HTML
        mensaje_html = f"""
        <div style="background-color: #f4f4f5; padding: 30px 15px; font-family: Arial, sans-serif;">
          <div style="max-width: 500px; margin: 0 auto; background-color: #ffffff; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.08);">
            
            <!-- Cabecera negra con tu Logo de Nexos -->
            <div style="background-color: #0c0c0c; padding: 28px 20px; text-align: center;">
              <img src="https://i.postimg.cc/NGkbyD4C/nexos2-0.png" alt="Logo Nexos" style="max-width: 140px; height: auto;" />
              <div style="width: 36px; height: 3px; background-color: #f57c00; margin: 12px auto 8px auto; border-radius: 2px;"></div>
              <p style="color: #e0e0e0; font-size: 12px; margin: 0;">Sistema de asistencia biométrica</p>
            </div>

            <!-- Cuerpo del mensaje -->
            <div style="padding: 32px 28px; color: #333333; line-height: 1.6;">
              <h2 style="color: #f57c00; margin-top: 0; font-size: 20px;">Hola, {usuario.nombre}</h2>
              <p style="font-size: 14px; color: #555555;">
                Recibimos una solicitud para restablecer la contraseña de tu cuenta. Haz clic en el siguiente botón para crear una nueva clave:
              </p>

              <!-- Botón Naranja -->
              <div style="text-align: center; margin: 28px 0;">
                <a href="{enlace}" style="background-color: #f37f0c; color: #ffffff; text-decoration: none; padding: 13px 28px; border-radius: 6px; font-weight: bold; font-size: 13px; letter-spacing: 0.8px; display: inline-block;">
                  RESTABLECER CONTRASEÑA
                </a>
              </div>

              <p style="font-size: 12.5px; color: #757575; margin-bottom: 0;">
                ⏱️ Este enlace es de un solo uso y expirará en <strong>15 minutos</strong>.<br>
                Si no solicitaste este cambio, puedes ignorar este mensaje con tranquilidad.
              </p>
            </div>

            <!-- Pie de correo -->
            <div style="background-color: #fafafa; padding: 14px 20px; text-align: center; border-top: 1px solid #eeeeee;">
              <p style="font-size: 11px; color: #9e9e9e; margin: 0;">
                © Nexos Tiendas SAC — Mensaje automático, no responder.
              </p>
            </div>

          </div>
        </div>
        """

        send_mail(
            subject='Restablecer contraseña - Sistema Nexos',
            message=mensaje_texto,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[correo],
            fail_silently=False,
            html_message=mensaje_html,
        )

        return Response(
            {'detail': 'Te enviamos un enlace de confirmación a tu correo.'},
            status=status.HTTP_200_OK
        )

class ConfirmarRecuperacionAPIView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        token = request.data.get('token')
        nueva_password = request.data.get('password')

        if not token or not nueva_password:
            return Response(
                {'detail': 'Datos incompletos para restablecer la contraseña.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # 900 segundos = 15 minutos de validez
            datos = signing.loads(token, salt=SALT_RECUPERACION, max_age=900)
        except signing.SignatureExpired:
            return Response(
                {'detail': 'El enlace ha expirado. Solicita uno nuevo.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except signing.BadSignature:
            return Response(
                {'detail': 'El enlace no es válido.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        usuario = Usuario.objects.filter(pk=datos.get('id_usuario'), estado=True).first()
        if not usuario:
            return Response(
                {'detail': 'Usuario no encontrado.'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Si el hash cambió, significa que este enlace ya se usó antes
        if usuario.password[:12] != datos.get('ph'):
            return Response(
                {'detail': 'Este enlace ya fue utilizado.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        usuario.set_password(nueva_password)
        usuario.save()

        return Response(
            {'detail': 'Contraseña actualizada correctamente.'},
            status=status.HTTP_200_OK
        )