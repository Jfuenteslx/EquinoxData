from django.urls import path
from . import views

app_name = 'productos'

urlpatterns = [
    path('', views.productos_view, name='productos_view'),

    # Insumos base
    path('insumos/', views.ProductoBaseListView.as_view(), name='producto-base-list'),
    path('insumos/nuevo/', views.producto_base_create, name='producto-base-create'),
    path('insumos/editar/<int:pk>/', views.producto_base_update, name='producto-base-update'),  
    path('insumos/eliminar/<int:pk>/', views.ProductoBaseDeleteView.as_view(), name='producto-base-delete'),

    # Productos del menu
    path('menu/', views.ProductoMenuListView.as_view(), name='producto-menu-list'),
    path('menu/nuevo/', views.producto_menu_create, name='producto-menu-create'),
    path('menu/editar/<int:pk>/', views.producto_menu_update, name='producto-menu-update'),
    path('menu/eliminar/<int:pk>/', views.ProductoMenuDeleteView.as_view(), name='producto-menu-delete'),
]