from django.urls import path
from . import views

app_name = 'eventos'

urlpatterns = [
    path('', views.listar_eventos, name='listar_eventos'),
    path('crear/', views.crear_evento, name='crear_evento'),
    path('actualizar/<int:pk>/', views.actualizar_evento, name='actualizar_evento'),
    path('eliminar/<int:pk>/', views.eliminar_evento, name='eliminar_evento'),
    path('crearcover/<int:evento_id>/', views.crear_cover, name='crear_cover'),
    path('editarcover/<int:cover_id>/', views.editar_cover, name='editar_cover'),



]
