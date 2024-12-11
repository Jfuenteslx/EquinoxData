# analizador/urls.py

from django.urls import path
from . import views

app_name = 'analizador'

urlpatterns = [
    path('entrada/', views.recibir_y_obtener_recomendacion, name='entrada'),
    # path('evaluar-casos-similares/', views.evaluar_casos_similares_view, name='evaluar_casos_similares'),
    path('evaluar-casos/', views.evaluar_casos_similares_view, name='evaluar_casos'),
    
    path('generar-casos-historicos/', views.generar_casos_historicos, name='generar_casos_historicos'),
    
    
    path('consultar-casos/', views.consultar_casos, name='consultar_casos'),

    path('entrada/', views.recibir_y_obtener_recomendacion, name='entrada'),
    path('resultados/', views.mostrar_resultados, name='resultados'),
    path('evaluar-casos/', views.evaluar_casos_similares_view, name='evaluar_casos'),
    path('generar-casos-historicos/', views.generar_casos_historicos, name='generar_casos_historicos'),
    path('consultar-casos/', views.consultar_casos, name='consultar_casos'),

    # Otras URLs...
    path('buscar-casos/', views.buscar_casos_similares, name='buscar_casos'),

    path('generar-recomendacion/', views.generar_recomendacion, name='generar_recomendacion'),
]



