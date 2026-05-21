from django.urls import path
from . import views

app_name = 'ventas'

urlpatterns = [
    path('iniciar/', views.iniciar_sesion, name='iniciar_sesion'),
    path('error/', views.error_view, name='error'),
    path('sesiones/', views.sesiones_activas, name='sesiones_activas'),
    path('cerrar/<int:sesion_id>/', views.cerrar_sesion, name='cerrar_sesion'),
    path('detalle/<int:sesion_id>/', views.detalle_sesion, name='detalle_sesion'),
    path('registrar/', views.registrar_venta, name='registrar_venta'),
    path('consolidar/', views.ventas_totales_del_dia, name='ventas_totales_del_dia'),
    path('consolidaciones/', views.revisar_consolidaciones, name='revisar_consolidaciones'),
]