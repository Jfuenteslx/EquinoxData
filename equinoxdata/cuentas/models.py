from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class CierreDiario(models.Model):
    ESTADO_CHOICES = [
        ('borrador', 'Borrador'),
        ('cerrado', 'Cerrado'),
    ]

    fecha = models.DateField(unique=True)
    evento = models.ForeignKey(
        'eventos.Evento',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='cierres'
    )
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='borrador')

    # --- Caja chica ---
    caja_inicial = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        help_text="Monto en caja chica al inicio del día (CAJA DIARIA)"
    )
    caja_hay = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Arqueo real de caja al cierre (HAY)"
    )

    # --- Ingresos ventas ---
    ingresos_ventas_manual = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Total de ventas ingresado manualmente"
    )
    usar_ventas_manual = models.BooleanField(default=True)

    # --- Pedido semanal ---
    monto_pedido_semanal = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    observacion_pedido = models.TextField(blank=True)
    observaciones = models.TextField(blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cierre diario"
        verbose_name_plural = "Cierres diarios"
        ordering = ['-fecha']

    def __str__(self):
        return f"Cierre {self.fecha}"

    @property
    def ingresos_ventas(self):
        if self.usar_ventas_manual or self.ingresos_ventas_manual is not None:
            return self.ingresos_ventas_manual or Decimal('0')
        try:
            from ventas.models import Consolidacion
            consolidacion = Consolidacion.objects.filter(fecha=self.fecha).first()
            if consolidacion and consolidacion.resumen_ventas:
                return sum(
                    Decimal(str(v.get('total', 0)))
                    for v in consolidacion.resumen_ventas.values()
                )
        except Exception:
            pass
        return Decimal('0')

    @property
    def total_otros_ingresos(self):
        return self.otros_ingresos.aggregate(
            total=models.Sum('monto'))['total'] or Decimal('0')

    @property
    def total_ingresos(self):
        return self.ingresos_ventas + self.total_otros_ingresos

    @property
    def total_gastos_diarios(self):
        return self.gastos_diarios.aggregate(
            total=models.Sum('monto'))['total'] or Decimal('0')

    @property
    def total_egresos_compras(self):
        total_manual = self.egresos_grandes.aggregate(
            total=models.Sum('monto'))['total'] or Decimal('0')
        if not self.usar_ventas_manual:
            try:
                from compras.models import Compra
                compras_efectivo = Compra.objects.filter(
                    fecha=self.fecha, metodo_pago='efectivo')
                return Decimal(str(sum(c.total for c in compras_efectivo)))
            except Exception:
                pass
        return total_manual

    @property
    def total_sueldos(self):
        return self.sueldos.aggregate(
            total=models.Sum('total_sueldo'))['total'] or Decimal('0')

    @property
    def total_bancos(self):
        return self.cierres_bancarios.aggregate(
            total=models.Sum('monto'))['total'] or Decimal('0')

    # Desglose de entregas por método de pago (meseras + barra)
    @property
    def total_efectivo_entregas(self):
        return self.entregas_meseras.aggregate(
            total=models.Sum('efectivo'))['total'] or Decimal('0')

    @property
    def total_qr_entregas(self):
        return self.entregas_meseras.aggregate(
            total=models.Sum('qr'))['total'] or Decimal('0')

    @property
    def total_voucher_entregas(self):
        return self.entregas_meseras.aggregate(
            total=models.Sum('voucher_banco'))['total'] or Decimal('0')

    @property
    def caja_debe(self):
        return (
            self.caja_inicial
            + (self.ingresos_ventas * Decimal('0.01'))
            - self.total_gastos_diarios
        )

    @property
    def caja_af_ec(self):
        if self.caja_hay is None:
            return None
        return self.caja_hay - self.caja_debe

    @property
    def caja_siguiente_dia(self):
        return self.caja_hay

    @property
    def total_neto(self):
        return (
            self.ingresos_ventas
            + self.total_otros_ingresos
            - self.total_egresos_compras
            - self.total_sueldos
            - self.total_gastos_diarios
            - self.total_bancos
        )


class OtroIngreso(models.Model):
    CONCEPTO_CHOICES = [
        ('ropa', 'Ropa'),
        ('merchandising', 'Merchandising'),
        ('equi_16', 'Equi 16%'),
        ('otro', 'Otro'),
    ]

    cierre = models.ForeignKey(CierreDiario, on_delete=models.CASCADE, related_name='otros_ingresos')
    concepto = models.CharField(max_length=20, choices=CONCEPTO_CHOICES)
    concepto_otro = models.CharField(max_length=100, blank=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])

    class Meta:
        verbose_name = "Otro ingreso"
        verbose_name_plural = "Otros ingresos"

    def __str__(self):
        return f"{self.get_concepto_display()} — {self.monto} bs"


class GastoDiario(models.Model):
    cierre = models.ForeignKey(CierreDiario, on_delete=models.CASCADE, related_name='gastos_diarios')
    concepto = models.CharField(max_length=200)
    monto = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])

    class Meta:
        verbose_name = "Gasto diario"
        verbose_name_plural = "Gastos diarios"

    def __str__(self):
        return f"{self.concepto} — {self.monto} bs"


class EgresoGrande(models.Model):
    CONCEPTO_CHOICES = [
        ('pedido', 'Pedido'),
        ('cocas', 'Cocas/Insumos'),
        ('logistica', 'Logística'),
        ('otro', 'Otro'),
    ]

    cierre = models.ForeignKey(CierreDiario, on_delete=models.CASCADE, related_name='egresos_grandes')
    concepto = models.CharField(max_length=20, choices=CONCEPTO_CHOICES)
    concepto_otro = models.CharField(max_length=200, blank=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    observacion = models.CharField(max_length=300, blank=True)

    class Meta:
        verbose_name = "Egreso grande"
        verbose_name_plural = "Egresos grandes"

    def __str__(self):
        return f"{self.get_concepto_display()} — {self.monto} bs"


class SueldoNoche(models.Model):
    TIPO_CHOICES = [
        ('porcentaje', 'Porcentaje de caja'),
        ('fijo', 'Monto fijo'),
    ]

    cierre = models.ForeignKey(CierreDiario, on_delete=models.CASCADE, related_name='sueldos')

    # Empleado registrado en el sistema (meseras/bartenders)
    empleado = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.PROTECT,
        related_name='sueldos_noche',
        null=True, blank=True
    )
    # Personal sin usuario en el sistema
    nombre_libre = models.CharField(max_length=100, blank=True)
    puesto = models.CharField(max_length=100, blank=True)

    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)

    # Para meseros (porcentaje de caja)
    caja_mesero = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    porcentaje = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    # Para staff fijo
    monto_fijo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_sueldo = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=0)
    observacion = models.CharField(max_length=300, blank=True)

    class Meta:
        verbose_name = "Sueldo de noche"
        verbose_name_plural = "Sueldos de noche"

    def __str__(self):
        nombre = self.empleado.username if self.empleado else self.nombre_libre
        return f"{nombre} — {self.total_sueldo} bs"

    def nombre_display(self):
        if self.empleado:
            return self.empleado.get_full_name() or self.empleado.username
        return self.nombre_libre

    def calcular_total(self):
        if self.tipo == 'porcentaje' and self.caja_mesero and self.porcentaje:
            caja = Decimal(str(self.caja_mesero))
            pct = Decimal(str(self.porcentaje))
            bruto = caja * (pct / Decimal('100'))
            return max(bruto - Decimal(str(self.descuento)), Decimal('0'))
        elif self.tipo == 'fijo' and self.monto_fijo:
            return max(Decimal(str(self.monto_fijo)) - Decimal(str(self.descuento)), Decimal('0'))
        return Decimal('0')

    def save(self, *args, **kwargs):
        self.total_sueldo = self.calcular_total()
        super().save(*args, **kwargs)


class EntregaMesera(models.Model):
    """
    Declaración de entrega al cierre de turno.
    Cubre meseras, barra, y cualquier persona que maneje caja.
    """

    cierre = models.ForeignKey(CierreDiario, on_delete=models.CASCADE, related_name='entregas_meseras')

    # Usuario del sistema (meseras y bartenders)
    usuario = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.PROTECT,
        related_name='entregas',
        null=True, blank=True
    )
    es_barra = models.BooleanField(
        default=False,
        help_text="True si esta entrega corresponde a la barra"
    )

    # Desglose de entrega
    efectivo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    qr = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="QR")
    voucher_banco = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Comprobante
    comprobante = models.ImageField(upload_to='comprobantes/%Y/%m/', null=True, blank=True)

    # Total talonario (Fase 1: manual; Fase 2: del sistema)
    total_talonario = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    observacion = models.CharField(max_length=300, blank=True)

    class Meta:
        verbose_name = "Entrega"
        verbose_name_plural = "Entregas"
        unique_together = [['cierre', 'usuario', 'es_barra']]

    def __str__(self):
        nombre = self.usuario.username if self.usuario else "Barra"
        return f"{nombre} — cierre {self.cierre.fecha}"

    def nombre_display(self):
        if self.es_barra:
            return "Barra"
        return self.usuario.get_full_name() or self.usuario.username if self.usuario else "—"

    @property
    def total_entregado(self):
        return self.efectivo + self.qr + self.voucher_banco

    @property
    def diferencia(self):
        if self.total_talonario is None:
            return None
        return self.total_entregado - self.total_talonario


class CierreBancario(models.Model):
    CUENTA_CHOICES = [
        ('equi_c1', 'Equi C1'),
        ('equi_c2', 'Equi C2'),
        ('equi_c3', 'Equi C3'),
    ]

    cierre = models.ForeignKey(CierreDiario, on_delete=models.CASCADE, related_name='cierres_bancarios')
    cuenta = models.CharField(max_length=20, choices=CUENTA_CHOICES)
    lote = models.CharField(max_length=50)
    monto = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])

    class Meta:
        verbose_name = "Cierre bancario"
        verbose_name_plural = "Cierres bancarios"

    def __str__(self):
        return f"{self.get_cuenta_display()} lote {self.lote} — {self.monto} bs"


class ResumenSemanal(models.Model):
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    nombre = models.CharField(max_length=100, blank=True)
    cierres = models.ManyToManyField(CierreDiario, related_name='resumenes')
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Resumen semanal"
        verbose_name_plural = "Resúmenes semanales"
        ordering = ['-fecha_inicio']

    def __str__(self):
        return self.nombre or f"Semana {self.fecha_inicio} — {self.fecha_fin}"

    def calcular_totales(self):
        cierres = self.cierres.all()
        return {
            'total_ventas': sum(c.ingresos_ventas for c in cierres),
            'total_otros_ingresos': sum(c.total_otros_ingresos for c in cierres),
            'total_ingresos': sum(c.total_ingresos for c in cierres),
            'total_gastos_diarios': sum(c.total_gastos_diarios for c in cierres),
            'total_egresos_compras': sum(c.total_egresos_compras for c in cierres),
            'total_sueldos': sum(c.total_sueldos for c in cierres),
            'total_bancos': sum(c.total_bancos for c in cierres),
            'total_neto': sum(c.total_neto for c in cierres),
            'noches': cierres.count(),
        }