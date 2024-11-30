# analizador/urls.py

from django.urls import path
from . import views

app_name = 'analizador'

urlpatterns = [
    path('entrada/', views.recibir_y_obtener_recomendacion, name='entrada'),
    path('evaluar-casos-similares/', views.evaluar_casos_similares_view, name='evaluar_casos_similares'),
    
    path('generar-casos-historicos/', views.generar_casos_historicos, name='generar_casos_historicos'),
    
    
    path('consultar-casos/', views.consultar_casos, name='consultar_casos'),
]
