from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from usuarios.models import Usuario
from productos.models import ProductoBase


class Pedido(models.Model):
    """Solicitud de compra elaborada por el jefe de barra."""

    TIPO_CHOICES = [
        ('planificacion', 'Planificación'),
        ('reposicion', 'Reposición'),
        ('extraordinario', 'Extraordinario'),
    ]

    ESTADO_CHOICES = [
        ('borrador', 'Borrador'),
        ('aprobado', 'Aprobado'),
        ('en_proceso', 'En proceso'),
        ('cerrado', 'Cerrado'),
    ]

    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='planificacion')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='borrador')
    fecha_solicitud = models.DateField(default=timezone.now)
    fecha_requerida = models.DateField(
        null=True, blank=True,
        help_text="Fecha para la que se necesita el pedido."
    )
    solicitado_por = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='pedidos'
    )
    monto_aprobado = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        help_text="Monto entregado al jefe de barra para ejecutar el pedido."
    )
    # Solo para pedidos extraordinarios
    cierre_diario = models.ForeignKey(
        'cuentas.CierreDiario',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='pedidos_extraordinarios',
        help_text="Cierre diario al que pertenece (solo para pedidos extraordinarios)."
    )
    observaciones = models.TextField(blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ['-fecha_solicitud']

    def __str__(self):
        return f"Pedido #{self.id} — {self.get_tipo_display()} — {self.fecha_solicitud}"

    @property
    def total_referencial(self):
        return sum(item.subtotal_referencial for item in self.items.all())
    
    @property
    def total_efectivo(self):
        from decimal import Decimal
        return sum(
            item.subtotal_referencial for item in self.items.all()
            if item.metodo_pago == 'efectivo'
        ) or Decimal('0')

    @property
    def total_transferencia(self):
        from decimal import Decimal
        return sum(
            item.subtotal_referencial for item in self.items.all()
            if item.metodo_pago == 'transferencia'
        ) or Decimal('0')

    @property
    def total_credito(self):
        from decimal import Decimal
        return sum(
            item.subtotal_referencial for item in self.items.all()
            if item.metodo_pago == 'credito'
        ) or Decimal('0')

    @property
    def total_comprado(self):
        return sum(
            compra.total for compra in self.compras.all()
        )

    @property
    def diferencia(self):
        return self.monto_aprobado - self.total_comprado


class ItemPedido(models.Model):
    """Ítem individual dentro de un pedido."""

    METODO_PAGO_CHOICES = [
        ('efectivo', 'Efectivo'),
        ('transferencia', 'Transferencia'),
        ('credito', 'Crédito'),
    ]

    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='items'
    )
    proveedor = models.CharField(
        max_length=100,
        help_text="Nombre del proveedor (ej: DYM, INNOBE/ACTRA)."
    )
    producto = models.ForeignKey(
        ProductoBase,
        on_delete=models.CASCADE,
        related_name='items_pedido'
    )
    cantidad_solicitada = models.IntegerField(default=1)
    precio_referencial = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        help_text="Precio estimado de referencia."
    )
    metodo_pago = models.CharField(
        max_length=20,
        choices=METODO_PAGO_CHOICES,
        default='transferencia'
    )

    class Meta:
        verbose_name = "Item de Pedido"
        verbose_name_plural = "Items de Pedido"

    def __str__(self):
        return f"{self.cantidad_solicitada} x {self.producto.nombre} — {self.proveedor}"

    @property
    def subtotal_referencial(self):
        return self.cantidad_solicitada * self.precio_referencial

    def clean(self):
        if self.cantidad_solicitada <= 0:
            raise ValidationError("La cantidad debe ser mayor que cero.")


class Compra(models.Model):
    """Cabecera de una compra de insumos."""

    METODO_PAGO_CHOICES = [
        ('efectivo', 'Efectivo'),
        ('transferencia', 'Transferencia'),
        ('credito', 'Crédito'),
    ]

    fecha = models.DateTimeField(default=timezone.now)
    personal = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='compras'
    )
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='compras',
        help_text="Pedido al que pertenece esta compra (opcional)."
    )
    proveedor = models.CharField(
        max_length=100, blank=True,
        help_text="Proveedor de esta compra."
    )
    metodo_pago = models.CharField(
        max_length=20,
        choices=METODO_PAGO_CHOICES,
        default='efectivo'
    )
    observaciones = models.TextField(blank=True, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name = "Compra"
        verbose_name_plural = "Compras"
        ordering = ['-fecha']

    def __str__(self):
        return f"Compra #{self.id} — {self.fecha.strftime('%d/%m/%Y')} por {self.personal.username}"

    def calcular_total(self):
        self.total = sum(item.subtotal for item in self.detalles.all())
        self.save()


class DetalleCompra(models.Model):
    """Detalle de cada insumo comprado."""

    compra = models.ForeignKey(
        Compra,
        on_delete=models.CASCADE,
        related_name='detalles'
    )
    producto = models.ForeignKey(
        ProductoBase,
        on_delete=models.CASCADE,
        related_name='compras'
    )
    cantidad_botellas = models.IntegerField(
        help_text="Cantidad de botellas o unidades compradas."
    )
    precio_unitario = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Precio real pagado por botella o unidad."
    )

    class Meta:
        verbose_name = "Detalle de Compra"
        verbose_name_plural = "Detalles de Compra"

    @property
    def subtotal(self):
        return self.cantidad_botellas * self.precio_unitario

    def __str__(self):
        return f"{self.cantidad_botellas} x {self.producto.nombre} @ Bs.{self.precio_unitario}"

    def clean(self):
        if self.cantidad_botellas <= 0:
            raise ValidationError("La cantidad debe ser mayor que cero.")
        if self.precio_unitario <= 0:
            raise ValidationError("El precio debe ser mayor que cero.")


class GastoOperativo(models.Model):
    """Gastos que no tocan inventario pero deben rendirse y contrastarse."""

    CATEGORIA_CHOICES = [
        ('limpieza', 'Limpieza'),
        ('logistica', 'Logística'),
        ('alimentacion', 'Alimentación'),
        ('mantenimiento', 'Mantenimiento'),
        ('otro', 'Otro'),
    ]

    METODO_PAGO_CHOICES = [
        ('efectivo', 'Efectivo'),
        ('transferencia', 'Transferencia'),
        ('credito', 'Crédito'),
    ]

    fecha = models.DateField(default=timezone.now)
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)
    proveedor = models.CharField(max_length=100, blank=True)
    descripcion = models.CharField(max_length=200)
    cantidad = models.DecimalField(max_digits=8, decimal_places=2, default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pago = models.CharField(max_length=20, choices=METODO_PAGO_CHOICES, default='efectivo')

    # Destino — uno de los dos debe estar presente
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='gastos_operativos'
    )

    compra = models.ForeignKey(
    'Compra',
    on_delete=models.SET_NULL,
    null=True, blank=True,
    related_name='gastos_operativos'
)

    cierre_diario = models.ForeignKey(
        'cuentas.CierreDiario',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='gastos_operativos'
    )

    registrado_por = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        related_name='gastos_operativos'
    )
    observaciones = models.CharField(max_length=300, blank=True)

    class Meta:
        verbose_name = "Gasto Operativo"
        verbose_name_plural = "Gastos Operativos"
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.descripcion} — {self.subtotal} bs ({self.fecha})"

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario