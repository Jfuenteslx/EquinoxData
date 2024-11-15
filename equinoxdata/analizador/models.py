from django.db import models
from compras.models import Pedido  # Importa Pedido desde la app compras
from eventos.models import Evento
from ventas.models import Cuenta
from inventarios.models import RegistroStock


# Modelo Casos para el sistema experto
class Caso(models.Model):
    cuentas = models.ForeignKey(Cuenta, on_delete=models.CASCADE, related_name='casos')  # Relacionado con la tabla Cuentas
    stock = models.ForeignKey(RegistroStock, on_delete=models.CASCADE, related_name='casos')  # Relacionado con la tabla RegistroStock
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='casos')  # Relacionado con la tabla Pedido
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='casos')  # Relacionado con la tabla Evento
    
    performance = models.IntegerField()  # Datos adicionales para el sistema experto
    label1 = models.CharField(max_length=15)
    label2 = models.CharField(max_length=15)

    class Meta:
        verbose_name = 'Caso'
        verbose_name_plural = 'Casos'

    def __str__(self):
        return f"Caso para el evento {self.evento.nombre} - Performance: {self.performance}"
