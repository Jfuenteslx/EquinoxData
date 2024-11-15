from django.urls import path
from . import views

app_name = 'inventarios'

urlpatterns = [
    path('', views.listar_inventarios, name='listar_inventarios'),
    path('agregar/', views.agregar_inventario, name='agregar_inventario'),
    path('actualizar/<int:inventario_id>/', views.actualizar_inventario, name='actualizar_inventario'),
    path('eliminar/<int:inventario_id>/', views.eliminar_inventario, name='eliminar_inventario'),
    path('registrar_stock/', views.registrar_stock, name='registrar_stock'),
]
