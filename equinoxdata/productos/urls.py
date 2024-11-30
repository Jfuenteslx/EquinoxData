from django.urls import path
from . import views
from .views import (
    PresentacionProductoListView,
    PresentacionProductoCreateView,
    PresentacionProductoUpdateView,
    PresentacionProductoDeleteView,
)

app_name = 'productos'

urlpatterns = [
    path('', views.productosview, name='productosview'),

    # Rutas para producto base
    path('listarbase/', views.listar_producto_base, name='listar_base'),  # Listar productos base
    path('crearbase/', views.crear_producto, name='crear_base'),  # Crear producto base
    path('editarbase/', views.editar_producto, name='editar_base'),  # Editar producto base
    path('eliminarbase/', views.eliminar_producto, name='eliminar_base'),  # Eliminar producto base

    # Rutas para recetas
    path('recetas/', views.listar_recetas, name='listar_recetas'),
    path('recetas/crear/', views.crear_receta, name='crear_receta'),
    path('recetas/editar/<int:pk>/', views.editar_receta, name='editar_receta'),
    path('recetas/eliminar/<int:pk>/', views.eliminar_receta, name='eliminar_receta'),

    # Rutas para presentaciones de productos
    path('presentaciones/', PresentacionProductoListView.as_view(), name='listar_presentaciones'),
    path('presentaciones/crear/', PresentacionProductoCreateView.as_view(), name='crear_presentacion_producto'),
    path('presentaciones/editar/<int:pk>/', PresentacionProductoUpdateView.as_view(), name='editar_presentacion_producto'),
    path('presentaciones/eliminar/<int:pk>/', PresentacionProductoDeleteView.as_view(), name='eliminar_presentacion_producto'),
]
