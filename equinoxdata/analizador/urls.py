from django.urls import path
from . import views

app_name = 'analizador'

urlpatterns = [
    path('entrada/', views.recibir_y_obtener_recomendacion, name='entrada'),
    path('resultados/', views.mostrar_resultados, name='resultados'),
    path('evaluar-casos/', views.evaluar_casos_similares_view, name='evaluar_casos'),
    path('buscar-casos/', views.buscar_casos_similares, name='buscar_casos'),
    path('consultar-casos/', views.consultar_casos, name='consultar_casos'),
    path('generar-casos/', views.generar_casos_historicos, name='generar_casos_historicos'),
    path('recomendacion/', views.generar_recomendacion, name='generar_recomendacion'),
]