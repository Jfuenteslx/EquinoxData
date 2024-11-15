from django.urls import path
from . import views



app_name = 'productos'
urlpatterns = [
    path('', views.productos_view, name='productos_view'),
    path('insumos/', views.listar_productos, name='listar_productos'),  # Lista de productos
    path('insumos/crear/', views.crear_producto, name='crear_producto'),  # Crear producto
    path('insumos/editar/<int:pk>/', views.editar_producto, name='editar_producto'),  # Editar producto
    path('insumos/eliminar/<int:pk>/', views.eliminar_producto, name='eliminar_producto'),  # Eliminar producto
    # Urls para el crud carta
    path('carta/', views.listar_presentaciones, name='listar_presentaciones'),
    path('carta/crear/', views.crear_presentacion, name='crear_presentacion'),
    path('carta/editar/<int:pk>/', views.editar_presentacion, name='editar_presentacion'),
    path('carta/eliminar/<int:pk>/', views.eliminar_presentacion, name='eliminar_presentacion'),
 # URLs para el CRUD de recetas
    path('recetas/', views.listar_recetas, name='listar_recetas'),
    path('recetas/crear/', views.crear_receta, name='crear_receta'),
    path('recetas/editar/<int:pk>/', views.editar_receta, name='editar_receta'),
    path('recetas/eliminar/<int:pk>/', views.eliminar_receta, name='eliminar_receta'),  # Eliminar receta

]
