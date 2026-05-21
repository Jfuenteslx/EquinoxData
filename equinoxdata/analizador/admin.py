from django.contrib import admin
from .models import CasoHistorico, ParametrosEntrada, Parametro, RecomendacionCompra


class CasoHistoricoAdmin(admin.ModelAdmin):
    list_display = ('evento', 'tipo_evento', 'genero_musical', 'promociones', 'coeficiente', 'performance', 'fecha_creacion')


admin.site.register(CasoHistorico, CasoHistoricoAdmin)
admin.site.register(ParametrosEntrada)
admin.site.register(Parametro)
admin.site.register(RecomendacionCompra)