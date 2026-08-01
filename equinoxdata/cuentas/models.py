from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class CierreDiario(models.Model):
    """
    Contenedor de una noche de operación.
    No almacena cálculos — todo se calcula desde los modelos relacionados.
    """
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
    caja_inicial = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        help_text="Saldo inicial del fondo de caja chica al abrir la noche."
    )
    observaciones = models.TextField(blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cierre diario"
        verbose_name_plural = "Cierres diarios"
        ordering = ['-fecha']

    def __str__(self):
        return f"Cierre {self.fecha}"

    # ------------------------------------------------------------------ #
    # Ingresos                                                             #
    # ------------------------------------------------------------------ #

    @property
    def total_ventas(self):
        """Suma de talonarios declarados por todos los puntos de venta."""
        return self.entregas_punto_venta.aggregate(
            total=models.Sum('total_talonario')
        )['total'] or Decimal('0')

    @property
    def total_efectivo(self):
        return self.entregas_punto_venta.aggregate(
            total=models.Sum('efectivo')
        )['total'] or Decimal('0')

    @property
    def total_qr(self):
        return self.entregas_punto_venta.aggregate(
            total=models.Sum('qr')
        )['total'] or Decimal('0')

    @property
    def total_voucher(self):
        return self.entregas_punto_venta.aggregate(
            total=models.Sum('voucher_banco')
        )['total'] or Decimal('0')

    @property
    def total_otros_ingresos(self):
        return self.otros_ingresos.aggregate(
            total=models.Sum('monto')
        )['total'] or Decimal('0')

    @property
    def total_ingresos(self):
        return self.total_ventas + self.total_otros_ingresos

    # ------------------------------------------------------------------ #
    # Egresos                                                              #
    # ------------------------------------------------------------------ #

    @property
    def total_sueldos(self):
        return self.sueldos.aggregate(
            total=models.Sum('total_sueldo')
        )['total'] or Decimal('0')

    @property
    def total_egresos_grandes(self):
        return self.egresos_grandes.aggregate(
            total=models.Sum('monto')
        )['total'] or Decimal('0')

    @property
    def total_compras_extraordinarias(self):
        """Suma de compras efectivo de pedidos extraordinarios de esta noche."""
        try:
            from compras.models import Compra
            return Compra.objects.filter(
                pedido__cierre_diario=self,
                pedido__tipo='extraordinario',
                metodo_pago='efectivo'
            ).aggregate(total=models.Sum('total'))['total'] or Decimal('0')
        except Exception:
            return Decimal('0')

    @property
    def total_gastos_operativos_noche(self):
        """Suma de gastos operativos de pedidos extraordinarios de esta noche."""
        try:
            from compras.models import GastoOperativo
            return GastoOperativo.objects.filter(
                cierre_diario=self
            ).aggregate(
                total=models.Sum(models.F('cantidad') * models.F('precio_unitario'))
            )['total'] or Decimal('0')
        except Exception:
            return Decimal('0')

    # ------------------------------------------------------------------ #
    # Caja chica                                                           #
    # ------------------------------------------------------------------ #

    @property
    def reposicion_caja_chica(self):
        """1% de las ventas brutas para reponer el fondo de caja chica."""
        return self.total_ventas * Decimal('0.01')

    @property
    def total_gastos_caja_chica(self):
        """Suma de egresos de caja chica de la noche."""
        return self.movimientos_caja_chica.filter(
            tipo='egreso'
        ).aggregate(
            total=models.Sum('monto')
        )['total'] or Decimal('0')

    @property
    def saldo_caja_chica(self):
        """Saldo esperado de caja chica al cierre."""
        return self.caja_inicial + self.reposicion_caja_chica - self.total_gastos_caja_chica

    # ------------------------------------------------------------------ #
    # Bancos                                                               #
    # ------------------------------------------------------------------ #

    @property
    def total_bancos(self):
        return self.cierres_bancarios.aggregate(
            total=models.Sum('monto')
        )['total'] or Decimal('0')

    # ------------------------------------------------------------------ #
    # Resultado                                                            #
    # ------------------------------------------------------------------ #

    @property
    def total_neto(self):
        return (
            self.total_ingresos
            - self.total_sueldos
            - self.total_egresos_grandes
            - self.total_compras_extraordinarias
            - self.total_gastos_operativos_noche
            - self.reposicion_caja_chica
        )


class EntregaPuntoVenta(models.Model):
    """
    Declaración de ventas y entrega de dinero por cada punto de venta
    (mesera o barra) al cierre del turno.
    """
    cierre = models.ForeignKey(
        CierreDiario,
        on_delete=models.CASCADE,
        related_name='entregas_punto_venta'
    )
    usuario = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.PROTECT,
        related_name='entregas_punto_venta',
        null=True, blank=True
    )
    es_barra = models.BooleanField(
        default=False,
        help_text="True si esta entrega corresponde a la barra."
    )

    # Desglose de entrega
    efectivo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    qr = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="QR")
    voucher_banco = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Total declarado del talonario
    total_talonario = models.DecimalField(
        max_digits=10, decimal_places=2,
        null=True, blank=True,
        help_text="Total de ventas según talonario."
    )

    comprobante = models.ImageField(
        upload_to='comprobantes/%Y/%m/',
        null=True, blank=True
    )
    observacion = models.CharField(max_length=300, blank=True)

    class Meta:
        verbose_name = "Entrega de punto de venta"
        verbose_name_plural = "Entregas de punto de venta"
        unique_together = [['cierre', 'usuario', 'es_barra']]

    def __str__(self):
        nombre = self.usuario.username if self.usuario else "Barra"
        return f"{nombre} — {self.cierre.fecha}"

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


class OtroIngreso(models.Model):
    """Ingresos adicionales de la noche (ropa, merch, cover, equi 16%, etc.)"""
    CONCEPTO_CHOICES = [
        ('ropa', 'Ropa'),
        ('merchandising', 'Merchandising'),
        ('cover', 'Cover / Entradas'),
        ('equi_16', 'Equi 16%'),
        ('otro', 'Otro'),
    ]

    cierre = models.ForeignKey(
        CierreDiario,
        on_delete=models.CASCADE,
        related_name='otros_ingresos'
    )
    concepto = models.CharField(max_length=20, choices=CONCEPTO_CHOICES)
    concepto_otro = models.CharField(max_length=100, blank=True)
    monto = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )

    class Meta:
        verbose_name = "Otro ingreso"
        verbose_name_plural = "Otros ingresos"

    def __str__(self):
        return f"{self.get_concepto_display()} — {self.monto} bs"


class MovimientoCajaChica(models.Model):
    """
    Historial de movimientos del fondo de caja chica.
    Reemplaza GastoDiario con un registro más completo.
    """
    TIPO_CHOICES = [
        ('egreso', 'Egreso'),
        ('ingreso', 'Ingreso'),
    ]

    cierre = models.ForeignKey(
        CierreDiario,
        on_delete=models.CASCADE,
        related_name='movimientos_caja_chica'
    )
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='egreso')
    concepto = models.CharField(max_length=200)
    monto = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    gasto_operativo = models.ForeignKey(
        'compras.GastoOperativo',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='movimientos_caja_chica',
        help_text="Gasto operativo asociado si aplica."
    )
    registrado_por = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        related_name='movimientos_caja_chica'
    )

    class Meta:
        verbose_name = "Movimiento de caja chica"
        verbose_name_plural = "Movimientos de caja chica"
        ordering = ['cierre__fecha']

    def __str__(self):
        return f"{self.get_tipo_display()} — {self.concepto} — {self.monto} bs"


class EgresoGrande(models.Model):
    """
    Salidas de dinero de la noche no relacionadas a compras de insumos.
    Ej: alquiler de equipo, pago a artista, retiro del dueño.
    """
    CONCEPTO_CHOICES = [
        ('alquiler_equipo', 'Alquiler de equipo'),
        ('pago_artista', 'Pago a artista/DJ'),
        ('retiro_dueno', 'Retiro del dueño'),
        ('cuetes', 'Cuetes/Pirotecnia'),
        ('decoracion', 'Decoración'),
        ('otro', 'Otro'),
    ]

    cierre = models.ForeignKey(
        CierreDiario,
        on_delete=models.CASCADE,
        related_name='egresos_grandes'
    )
    concepto = models.CharField(max_length=30, choices=CONCEPTO_CHOICES)
    concepto_otro = models.CharField(max_length=200, blank=True)
    monto = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    metodo_pago = models.CharField(
        max_length=20,
        choices=[('efectivo', 'Efectivo'), ('transferencia', 'Transferencia')],
        default='efectivo'
    )
    observacion = models.CharField(max_length=300, blank=True)

    class Meta:
        verbose_name = "Egreso grande"
        verbose_name_plural = "Egresos grandes"

    def __str__(self):
        return f"{self.get_concepto_display()} — {self.monto} bs"


class SueldoNoche(models.Model):
    """Pago de personal por noche."""
    TIPO_CHOICES = [
        ('porcentaje', 'Porcentaje de caja'),
        ('fijo', 'Monto fijo'),
    ]

    cierre = models.ForeignKey(
        CierreDiario,
        on_delete=models.CASCADE,
        related_name='sueldos'
    )
    empleado = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.PROTECT,
        related_name='sueldos_noche',
        null=True, blank=True
    )
    nombre_libre = models.CharField(max_length=100, blank=True)
    puesto = models.CharField(max_length=100, blank=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    caja_mesero = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    porcentaje = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
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


class CierreBancario(models.Model):
    """Cierres de POS por lote."""
    CUENTA_CHOICES = [
        ('equi_c1', 'Equi C1'),
        ('equi_c2', 'Equi C2'),
        ('equi_c3', 'Equi C3'),
    ]

    cierre = models.ForeignKey(
        CierreDiario,
        on_delete=models.CASCADE,
        related_name='cierres_bancarios'
    )
    cuenta = models.CharField(max_length=20, choices=CUENTA_CHOICES)
    lote = models.CharField(max_length=50)
    monto = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )

    class Meta:
        verbose_name = "Cierre bancario"
        verbose_name_plural = "Cierres bancarios"

    def __str__(self):
        return f"{self.get_cuenta_display()} lote {self.lote} — {self.monto} bs"


class GastoFijo(models.Model):
    """
    Gastos recurrentes del bar como negocio.
    No se asocian a ningún cierre diario — aparecen en el resumen semanal/mensual.
    """
    CONCEPTO_CHOICES = [
        ('luz', 'Luz'),
        ('agua', 'Agua'),
        ('alquiler', 'Alquiler'),
        ('prohigiene', 'Prohigiene'),
        ('internet', 'Internet'),
        ('otro', 'Otro'),
    ]

    METODO_PAGO_CHOICES = [
        ('efectivo', 'Efectivo'),
        ('transferencia', 'Transferencia'),
    ]

    concepto = models.CharField(max_length=20, choices=CONCEPTO_CHOICES)
    concepto_otro = models.CharField(max_length=100, blank=True)
    descripcion = models.CharField(max_length=200, blank=True)
    monto = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    fecha_pago = models.DateField()
    periodo_mes = models.IntegerField(help_text="Mes al que corresponde (1-12)")
    periodo_anio = models.IntegerField(help_text="Año al que corresponde")
    metodo_pago = models.CharField(max_length=20, choices=METODO_PAGO_CHOICES, default='transferencia')
    comprobante = models.ImageField(upload_to='gastos_fijos/%Y/%m/', null=True, blank=True)
    registrado_por = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        related_name='gastos_fijos'
    )

    class Meta:
        verbose_name = "Gasto fijo"
        verbose_name_plural = "Gastos fijos"
        ordering = ['-fecha_pago']

    def __str__(self):
        return f"{self.get_concepto_display()} — {self.monto} bs ({self.periodo_mes}/{self.periodo_anio})"


class ResumenSemanal(models.Model):
    """
    Agrupador de noches para el reporte semanal.
    Calcula en tiempo real — no almacena totales.
    """
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
        total_ventas = sum(c.total_ventas for c in cierres)
        total_otros = sum(c.total_otros_ingresos for c in cierres)
        total_sueldos = sum(c.total_sueldos for c in cierres)
        total_egresos = sum(c.total_egresos_grandes for c in cierres)
        total_compras_ext = sum(c.total_compras_extraordinarias for c in cierres)
        total_gastos_op = sum(c.total_gastos_operativos_noche for c in cierres)
        reposicion_cc = sum(c.reposicion_caja_chica for c in cierres)
        neto_operacional = sum(c.total_neto for c in cierres)

        # Gastos fijos del período
        from django.db.models import Sum
        gastos_fijos = GastoFijo.objects.filter(
            fecha_pago__gte=self.fecha_inicio,
            fecha_pago__lte=self.fecha_fin
        ).aggregate(total=Sum('monto'))['total'] or Decimal('0')

        return {
            'noches': cierres.count(),
            'total_ventas': total_ventas,
            'total_otros_ingresos': total_otros,
            'total_ingresos': total_ventas + total_otros,
            'total_sueldos': total_sueldos,
            'total_egresos_grandes': total_egresos,
            'total_compras_extraordinarias': total_compras_ext,
            'total_gastos_operativos': total_gastos_op,
            'reposicion_caja_chica': reposicion_cc,
            'neto_operacional': neto_operacional,
            'gastos_fijos': gastos_fijos,
            'neto_real': neto_operacional - gastos_fijos,
        }