from django.urls import path
from . import views

app_name = 'ventas'

urlpatterns = [
    # Sesiones
    path('', views.lista_sesiones, name='lista_sesiones'),
    path('abrir/', views.abrir_sesion, name='abrir_sesion'),
    path('sesion/<int:pk>/', views.sesion_activa, name='sesion_activa'),
    path('sesion/<int:pk>/cerrar/', views.cerrar_sesion, name='cerrar_sesion'),

    # Comandas
    path('sesion/<int:sesion_pk>/comanda/nueva/', views.crear_comanda, name='crear_comanda'),
    path('comanda/<int:comanda_pk>/lista/', views.marcar_lista, name='marcar_lista'),
    path('comanda/<int:comanda_pk>/entregada/', views.marcar_entregada, name='marcar_entregada'),
    path('comanda/<int:comanda_pk>/anular/', views.anular_comanda, name='anular_comanda'),
    path('sesion/<int:sesion_pk>/listas.json/', views.comandas_listas_json, name='comandas_listas_json'),

    # Vista barra
    path('barra/', views.vista_barra, name='vista_barra'),
    path('barra/comandas.json/', views.comandas_pendientes_json, name='comandas_pendientes_json'),

    # Consolidaciones
    path('consolidaciones/', views.lista_consolidaciones, name='lista_consolidaciones'),
    path('consolidacion/<int:pk>/', views.detalle_consolidacion, name='detalle_consolidacion'),
]