from django.urls import path
from . import views

app_name = 'compras'

urlpatterns = [
    path('crear/', views.crear_compra, name='crear_compra'),
    # Otras URLs relacionadas con compras
    path('consolidar/', views.consolidar_pedido, name='consolidar_pedido'),
    path('confirmar_consolidacion/', views.confirmar_consolidacion, name='confirmar_consolidacion'),
    path('registro_exitoso/', views.registro_exitoso, name='registro_exitoso'),

    path('eliminar/<int:compra_id>/', views.eliminar_compra, name='eliminar_compra'),

]
