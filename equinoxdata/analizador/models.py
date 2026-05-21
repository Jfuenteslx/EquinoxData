from django.db import models
from eventos.models import Evento


class CasoHistorico(models.Model):
    """
    Caso generado al consolidar un turno.
    Contiene toda la informacion necesaria para entrenar el sistema experto.
    """
    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        related_name='casos_historicos'
    )
    sesion = models.ForeignKey(
        'ventas.Consolidacion',
        on_delete=models.CASCADE,
        related_name='casos_historicos',
        null=True,
        blank=True
    )

    # Parametros del evento
    tipo_evento = models.CharField(max_length=255, default='Concierto')
    genero_musical = models.CharField(max_length=255, blank=True, null=True)
    promociones = models.CharField(max_length=255, default='Ninguna')

    # Variables difusas de entrada
    aforo_esperado = models.IntegerField(default=0)
    ventas_esperadas = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    consumo_per_capita = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Resultados del sistema experto
    coeficiente = models.FloatField(default=0.0)
    performance = models.FloatField(default=0.0)

    # JSON con el resumen de ventas e inventario del turno
    resumen_ventas = models.JSONField(default=dict)
    resumen_inventario = models.JSONField(default=dict)
    recomendacion_compra = models.JSONField(default=dict)

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Caso Historico"
        verbose_name_plural = "Casos Historicos"
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"Caso — {self.evento.nombre} ({self.evento.fecha.strftime('%d/%m/%Y')})"


class ParametrosEntrada(models.Model):
    """Parametros ingresados por el usuario para analizar un evento."""
    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        related_name='parametros'
    )
    aforo_esperado = models.IntegerField()
    ventas_esperadas = models.IntegerField()
    consumo_esperado = models.IntegerField()
    tipo_evento = models.CharField(max_length=255)
    genero_musical = models.CharField(max_length=255, blank=True, null=True)
    promociones = models.CharField(max_length=255, default='Ninguna')

    class Meta:
        verbose_name = "Parametros de Entrada"
        verbose_name_plural = "Parametros de Entrada"

    def __str__(self):
        return f"Parametros para {self.evento.nombre} ({self.evento.fecha.strftime('%d/%m/%Y')})"


class Parametro(models.Model):
    """Parametro configurable del sistema experto."""
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(
        max_length=50,
        choices=[
            ('desplegable', 'Desplegable'),
            ('difuso', 'Difuso')
        ]
    )
    opciones = models.JSONField(default=list)

    class Meta:
        verbose_name = "Parametro"
        verbose_name_plural = "Parametros"

    def __str__(self):
        return self.nombre


class RecomendacionCompra(models.Model):
    """Recomendacion de compra generada por el sistema experto."""
    evento = models.ForeignKey(
        Evento,
        on_delete=models.CASCADE,
        related_name='recomendaciones'
    )
    producto = models.CharField(max_length=255)
    cantidad_recomendada = models.IntegerField()
    fecha_generacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Recomendacion de Compra"
        verbose_name_plural = "Recomendaciones de Compra"

    def __str__(self):
        return f"Recomendacion: {self.producto} para {self.evento.nombre}"