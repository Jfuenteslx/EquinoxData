# usuarios/urls.py
from django.urls import path
from .views import login_view, administrar_usuarios, crear_usuario, editar_usuario, eliminar_usuario,dashboard_view
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login/', login_view, name='login'),
    path('administrar/', administrar_usuarios, name='administrar_usuarios'),
    path('crear/', crear_usuario, name='crear_usuario'),
    path('editar/<int:usuario_id>/', editar_usuario, name='editar_usuario'),
    path('eliminar/<int:usuario_id>/', eliminar_usuario, name='eliminar_usuario'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # estos son para la demo
    path('', views.inicio_view, name='inicio'),
    path('ventas/nueva/', views.nueva_venta_view, name='nueva_venta'),
    path('ventas/editar-comanda/', views.editar_comanda_view, name='editar_comanda'),
    path('ventas/reportes/', views.reportes_ventas_view, name='reportes_ventas'),
    path('ventas/consolidar/', views.consolidar_view, name='consolidar'),
    path('pedidos/', views.pedidos_view, name='pedidos'),
    path('inventario/registrar-compras/', views.registrar_compras_view, name='registrar_compras'),
    path('inventario/registrar-saldos/', views.registrar_saldos_view, name='registrar_saldos'),
    path('inventario/productos/', views.productos_view, name='productos'),
    path('inventario/reportes/', views.reportes_inventario_view, name='reportes_inventario'),
    path('agenda/administrar-eventos/', views.administrar_eventos_view, name='administrar_eventos'),
    path('reportes/consultar-casos/', views.consultar_casos_view, name='consultar_casos'),
    path('reportes/analizar-eventos/', views.analizar_eventos_view, name='analizar_eventos'),
    path('personal/', views.personal_view, name='personal'),
]
