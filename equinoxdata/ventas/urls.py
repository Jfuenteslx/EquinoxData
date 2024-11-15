


# urls.py

from django.urls import path
from . import views

app_name = 'ventas'  # Asegúrate de que esta línea esté presente

urlpatterns = [
    path('iniciar/', views.iniciar_sesion, name='iniciar_sesion'),
    path('error/', views.error_view, name='error'),
    path('sesiones/', views.sesiones_activas, name='sesiones_activas'),
    path('cerrar_sesion/<int:sesion_id>/', views.cerrar_sesion, name='cerrar_sesion'),
    path('detalle/<int:sesion_id>/', views.detalle_sesion, name='detalle_sesion'),
    
    path('registrar/', views.registrar_venta, name='registrar_venta'),
    
    path('ventas_totales/', views.ventas_totales_del_dia, name='ventas_totales_del_dia'),
     # URL para revisar las cuentas consolidadas
    path('revisar_cuentas/', views.revisar_cuentas, name='revisar_cuentas'),

    # URL para consolidar una cuenta por fecha
    path('consolidar_cuenta/<str:fecha>/', views.consolidar_cuenta, name='consolidar_cuenta'),


    
]

