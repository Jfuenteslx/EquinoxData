from django.urls import path
from . import views

app_name = 'compras'

urlpatterns = [
    path('', views.crear_compra, name='crear_compra'),
    path('eliminar/<int:compra_id>/', views.eliminar_compra, name='eliminar_compra'),
]