from django.db import models
from compras.models import Pedido  # Importa Pedido desde la app compras
from eventos.models import Evento
from ventas.models import Cuenta
from inventarios.models import RegistroStock


class CasoHistorico(models.Model):
    evento = models.ForeignKey(
        Evento, on_delete=models.CASCADE, related_name="casos_históricos"
    )
    pedido = models.ForeignKey(
        Pedido, on_delete=models.CASCADE, related_name="casos_históricos"
    )
    cuenta = models.ForeignKey(
        Cuenta, on_delete=models.CASCADE, related_name="casos_históricos"
    )
    inventario = models.ForeignKey(
        RegistroStock, on_delete=models.CASCADE, related_name="casos_históricos"
    )
    
    tipo_evento = models.CharField(max_length=255, default='Ninguna')  # Tipo de evento
    show_presentado = models.CharField(max_length=255, default='Ninguna')  # Show presentado
    genero_musical = models.CharField(max_length=255, default='Ninguna', null=True, blank=True)  # Permite que sea NULL por ahora

    promociones = models.CharField(max_length=255, default='Ninguna')  # Promociones aplicadas

    coeficiente = models.FloatField(default=0.0)  # Resultado del cálculo de las variables difusas
    performance = models.FloatField(default=0.0)  # Porcentaje de evaluación del caso histórico

    def __str__(self):
        return f"Caso Histórico - Evento: {self.evento.nombre}, Fecha: {self.fecha_evento}"

    class Meta:
        verbose_name = "Caso Histórico"
        verbose_name_plural = "Casos Históricos"


class ParametrosEntrada(models.Model):
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE)
    aforo_esperado = models.IntegerField()  # Valor basado en el slider
    ventas_esperadas = models.IntegerField()  # Valor basado en el slider
    consumo_esperado = models.IntegerField()  # Valor basado en el slider
    tipo_evento = models.CharField(max_length=255)
    show_presentado = models.CharField(max_length=255)
    genero_musical = models.CharField(max_length=255)
    promociones = models.CharField(max_length=255)

    def __str__(self):
        return f"Parámetros para {self.evento.nombre} ({self.evento.fecha})"

    # analizador/models.py


from django.db import models


class Parametro(models.Model):
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(
        max_length=50, choices=[("desplegable", "Desplegable"), ("difuso", "Difuso")]
    )
    opciones = models.JSONField(
        default=list
    )  # Almacenaremos las opciones en un campo JSON

    def __str__(self):
        return self.nombre


class RecomendacionCompra(models.Model):
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE)
    producto = models.CharField(max_length=255)
    cantidad_recomendada = models.IntegerField()
    fecha_generacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Recomendación para {self.producto} en {self.evento.nombre}"
