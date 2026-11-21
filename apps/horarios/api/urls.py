from django.urls import path
from apps.horarios.api.views import (
    HorarioListCreateAPIView,
    HorarioDetailAPIView,
    AsignacionHorarioListCreateAPIView,
    AsignacionHorarioDeleteAPIView,
)

urlpatterns = [
    path('turnos/', HorarioListCreateAPIView.as_view(), name='horarios-turnos-list'),
    path('turnos/<int:id_horario>/', HorarioDetailAPIView.as_view(), name='horarios-turnos-detail'),
    path('asignaciones/', AsignacionHorarioListCreateAPIView.as_view(), name='horarios-asignaciones-list'),
    path('asignaciones/<int:id_asignacion>/', AsignacionHorarioDeleteAPIView.as_view(), name='horarios-asignaciones-delete'),
]