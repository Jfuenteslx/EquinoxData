from django.urls import path
from . import views

app_name = 'inventarios'

urlpatterns = [
    # Listado de inventarios
    path('', views.inventario_list, name='inventario_list'),
    # Inicialización de inventarios
    path('inicializar/', views.inicializar_inventarios, name='inicializar_inventarios'),


    # Actualización de inventarios
    path('actualizar/<int:producto_id>/<int:cantidad>/<str:tipo>/', views.actualizar_inventario, name='actualizar_inventario'),

    # Gestión de saldos
    path('saldos/', views.saldo_list, name='saldo_list'),
    path('saldos/nuevo/', views.saldo_create, name='saldo_create'),
    path('saldos/editar/<int:id>/', views.saldo_edit, name='saldo_edit'),
    path('saldos/eliminar/<int:id>/', views.saldo_delete, name='saldo_delete'),
    path('saldos/confirmar_eliminar/<int:id>/', views.saldo_confirm_delete, name='saldo_confirm_delete'),

    # Reportes adicionales de inventarios
    path('productos_bajo_stock/', views.productos_bajo_stock, name='productos_bajo_stock'),
    path('detalle_producto/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),
    path('consolidar/', views.consolidar_inventario, name='consolidar_inventario'),


    # Listado de inventarios
    path('', views.inventario_list, name='inventario_list'),
    path('<int:id>/historial/', views.inventario_historial, name='inventario_historial'),
]
