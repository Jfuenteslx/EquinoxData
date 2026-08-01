from django.urls import path
from . import views

app_name = 'cuentas'

urlpatterns = [
    # Cierres diarios
    path('', views.lista_cierres, name='lista_cierres'),
    path('nuevo/', views.crear_cierre, name='crear_cierre'),
    path('<int:pk>/', views.detalle_cierre, name='detalle_cierre'),
    path('<int:pk>/cerrar/', views.cerrar_cierre, name='cerrar_cierre'),

    # Otros ingresos
    path('<int:cierre_pk>/ingresos/agregar/', views.agregar_otro_ingreso, name='agregar_otro_ingreso'),
    path('ingresos/<int:pk>/eliminar/', views.eliminar_otro_ingreso, name='eliminar_otro_ingreso'),

    # Caja chica
    path('<int:cierre_pk>/caja/agregar/', views.agregar_movimiento_caja, name='agregar_movimiento_caja'),
    path('caja/<int:pk>/eliminar/', views.eliminar_movimiento_caja, name='eliminar_movimiento_caja'),

    # Egresos grandes
    path('<int:cierre_pk>/egresos/agregar/', views.agregar_egreso_grande, name='agregar_egreso_grande'),
    path('egresos/<int:pk>/eliminar/', views.eliminar_egreso_grande, name='eliminar_egreso_grande'),

    # Sueldos
    path('<int:cierre_pk>/sueldos/agregar/', views.agregar_sueldo, name='agregar_sueldo'),
    path('sueldos/<int:pk>/eliminar/', views.eliminar_sueldo, name='eliminar_sueldo'),

    # Entregas punto de venta
    path('<int:cierre_pk>/entregas/agregar/', views.agregar_entrega, name='agregar_entrega'),
    path('entregas/<int:pk>/editar/', views.editar_entrega, name='editar_entrega'),
    path('entregas/<int:pk>/eliminar/', views.eliminar_entrega, name='eliminar_entrega'),

    # Cierres bancarios
    path('<int:cierre_pk>/bancos/agregar/', views.agregar_cierre_bancario, name='agregar_cierre_bancario'),
    path('bancos/<int:pk>/eliminar/', views.eliminar_cierre_bancario, name='eliminar_cierre_bancario'),

    # Gastos fijos
    path('gastos-fijos/', views.lista_gastos_fijos, name='lista_gastos_fijos'),
    path('gastos-fijos/nuevo/', views.agregar_gasto_fijo, name='agregar_gasto_fijo'),
    path('gastos-fijos/<int:pk>/eliminar/', views.eliminar_gasto_fijo, name='eliminar_gasto_fijo'),

    # Resúmenes semanales
    path('resumenes/', views.lista_resumenes, name='lista_resumenes'),
    path('resumenes/nuevo/', views.crear_resumen, name='crear_resumen'),
    path('resumenes/<int:pk>/', views.detalle_resumen, name='detalle_resumen'),
]