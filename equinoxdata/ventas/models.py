from decimal import Decimal

from django.db import models
from django.utils import timezone

from usuarios.models import Usuario
from productos.models import ProductoMenu


def decimal_to_float(data):
    """Convierte valores Decimal en un diccionario o lista a float para serialización JSON."""
    if isinstance(data, dict):
        return {k: decimal_to_float(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [decimal_to_float(item) for item in data]
    elif isinstance(data, Decimal):
        return float(data)
    return data


class SesionDeTrabajo(models.Model):
    """Turno de trabajo de un usuario durante un evento."""

    ESTADO_CHOICES = [
        ('abierta', 'Abierta'),
        ('cerrada', 'Cerrada'),
    ]

    usuario_encargado = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='sesiones_trabajo'
    )
    evento = models.ForeignKey(
        'eventos.Evento',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sesiones'
    )
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='abierta')
    total_ventas = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name = "Sesion de Trabajo"
        verbose_name_plural = "Sesiones de Trabajo"
        ordering = ['-fecha_inicio']

    def __str__(self):
        return f"Sesion de {self.usuario_encargado.username} — {self.get_estado_display()}"

    def calcular_total_ventas(self):
        """Recalcula el total sumando todas las comandas de esta sesion."""
        from django.db.models import Sum
        total = self.comandas.aggregate(Sum('total'))['total__sum'] or 0
        self.total_ventas = total
        self.save(update_fields=['total_ventas'])

    def cerrar(self):
        """Cierra la sesion y registra la fecha de fin."""
        if self.estado == 'abierta':
            self.calcular_total_ventas()
            self.estado = 'cerrada'
            self.fecha_fin = timezone.now()
            self.save()


class Comanda(models.Model):
    """Registro de un producto vendido durante una sesion de trabajo."""

    sesion_de_trabajo = models.ForeignKey(
        SesionDeTrabajo,
        on_delete=models.CASCADE,
        related_name='comandas'
    )
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='comandas'
    )
    producto = models.ForeignKey(
        ProductoMenu,
        on_delete=models.CASCADE,
        related_name='comandas'
    )
    cantidad = models.PositiveIntegerField()
    total = models.DecimalField(max_digits=10, decimal_places=2)
    hora = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Comanda"
        verbose_name_plural = "Comandas"
        ordering = ['-hora']

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} — {self.usuario.username}"

    def save(self, *args, **kwargs):
        # Calcular total automaticamente antes de guardar
        self.total = self.producto.precio * self.cantidad
        super().save(*args, **kwargs)
        # Actualizar total de la sesion
        self.sesion_de_trabajo.calcular_total_ventas()


class Consolidacion(models.Model):
    """Resumen de ventas al cierre de un turno, listo para el analizador."""

    sesion = models.OneToOneField(
        SesionDeTrabajo,
        on_delete=models.CASCADE,
        related_name='consolidacion'
    )
    fecha = models.DateField(default=timezone.now)
    resumen = models.JSONField(
        default=dict,
        help_text="JSON con el resumen de ventas por producto."
    )
    consolidado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        related_name='consolidaciones'
    )
    fecha_consolidacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Consolidacion"
        verbose_name_plural = "Consolidaciones"
        ordering = ['-fecha']

    def __str__(self):
        return f"Consolidacion del {self.fecha} — Sesion #{self.sesion.id}"

    def generar_resumen(self):
        """Genera el JSON de resumen agrupando comandas por producto."""
        resumen = {}
        for comanda in self.sesion.comandas.all():
            nombre = comanda.producto.nombre
            if nombre not in resumen:
                resumen[nombre] = {
                    'producto_id': comanda.producto.id,
                    'tipo': comanda.producto.tipo,
                    'cantidad_total': 0,
                    'total_bs': Decimal('0.00'),
                }
            resumen[nombre]['cantidad_total'] += comanda.cantidad
            resumen[nombre]['total_bs'] += comanda.total

        self.resumen = decimal_to_float(resumen)
        self.save(update_fields=['resumen'])