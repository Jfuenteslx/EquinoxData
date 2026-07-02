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

    # Gastos diarios
    path('<int:cierre_pk>/gastos/agregar/', views.agregar_gasto_diario, name='agregar_gasto_diario'),
    path('gastos/<int:pk>/eliminar/', views.eliminar_gasto_diario, name='eliminar_gasto_diario'),

    # Egresos grandes
    path('<int:cierre_pk>/egresos/agregar/', views.agregar_egreso_grande, name='agregar_egreso_grande'),
    path('egresos/<int:pk>/eliminar/', views.eliminar_egreso_grande, name='eliminar_egreso_grande'),

    # Sueldos
    path('<int:cierre_pk>/sueldos/agregar/', views.agregar_sueldo, name='agregar_sueldo'),
    path('sueldos/<int:pk>/eliminar/', views.eliminar_sueldo, name='eliminar_sueldo'),

    # Entregas
    path('<int:cierre_pk>/entregas/agregar/', views.agregar_entrega_mesera, name='agregar_entrega_mesera'),
    path('entregas/<int:pk>/editar/', views.editar_entrega_mesera, name='editar_entrega_mesera'),
    path('entregas/<int:pk>/eliminar/', views.eliminar_entrega_mesera, name='eliminar_entrega_mesera'),

    # Cierres bancarios
    path('<int:cierre_pk>/bancos/agregar/', views.agregar_cierre_bancario, name='agregar_cierre_bancario'),
    path('bancos/<int:pk>/eliminar/', views.eliminar_cierre_bancario, name='eliminar_cierre_bancario'),

    # Resúmenes semanales
    path('resumenes/', views.lista_resumenes, name='lista_resumenes'),
    path('resumenes/nuevo/', views.crear_resumen, name='crear_resumen'),
    path('resumenes/<int:pk>/', views.detalle_resumen, name='detalle_resumen'),
]