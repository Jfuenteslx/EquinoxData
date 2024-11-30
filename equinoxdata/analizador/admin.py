from django.contrib import admin
from .models import CasoHistorico

class CasoHistoricoAdmin(admin.ModelAdmin):
    # Actualizamos list_display para mostrar los nuevos campos
    list_display = (
        'evento', 
        'tipo_evento', 
        'show_presentado', 
        'genero_musical', 
        'promociones', 
        'coeficiente', 
        'performance'
    )

    # Si quieres mostrar más detalles o permitir alguna funcionalidad adicional, puedes agregar más configuraciones aquí

admin.site.register(CasoHistorico, CasoHistoricoAdmin)
