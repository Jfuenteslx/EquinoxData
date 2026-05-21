from django.urls import path
from . import views

app_name = 'inventarios'

urlpatterns = [
    path('', views.inventario_list, name='inventario_list'),
    path('apertura/', views.apertura_diaria, name='apertura_diaria'),
    path('ajustar/<int:producto_id>/', views.ajustar_inventario, name='ajustar_inventario'),
    path('historial/', views.historial_movimientos, name='historial_movimientos'),
    path('historial/<int:producto_id>/', views.historial_movimientos, name='historial_producto'),
    path('saldos/', views.registrar_saldos, name='saldo_list'),
    path('saldos/registrar/', views.registrar_saldos, name='registrar_saldos'),
]