from django.urls import path
from . import views

app_name = 'compras'

urlpatterns = [
    # Pedidos
    path('pedidos/', views.lista_pedidos, name='lista_pedidos'),
    path('pedidos/nuevo/', views.crear_pedido, name='crear_pedido'),
    path('pedidos/<int:pedido_id>/', views.detalle_pedido, name='detalle_pedido'),
    path('pedidos/<int:pedido_id>/estado/', views.cambiar_estado_pedido, name='cambiar_estado_pedido'),

    # Compras
    path('', views.crear_compra, name='crear_compra'),
    path('eliminar/<int:compra_id>/', views.eliminar_compra, name='eliminar_compra'),
    path('gastos/', views.lista_gastos_operativos, name='lista_gastos_operativos'),
    path('gastos/nuevo/', views.crear_gasto_operativo, name='crear_gasto_operativo'),
]