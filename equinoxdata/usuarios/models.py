from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

# Modelo de Usuario personalizado
class Usuario(AbstractUser):
    correo = models.EmailField(unique=True)
    contraseña = models.CharField(max_length=100)

    # Especificar nombres para evitar conflictos en accesos inversos
    groups = models.ManyToManyField(
        Group,
        related_name='usuarios_user_set',  # Cambia este nombre según tus necesidades
        blank=True,
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name='usuarios_user_set',  # Cambia este nombre según tus necesidades
        blank=True,
    )

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return self.correo

# Tabla de Detalles del Personal
class Personal(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='personal')
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    CI = models.CharField(max_length=20, unique=True)  # Carnet de Identidad
    rol = models.CharField(max_length=50)  # Ej: admin, cliente, vendedor

    def __str__(self):
        return f"{self.nombre} {self.apellido} - {self.rol}"

# Tabla de Sesiones
class Sesion(models.Model):
    marca = models.DateTimeField(auto_now_add=True)
    personal = models.ForeignKey(Personal, on_delete=models.CASCADE, related_name='sesiones')

# Tabla de Ventas
class Ventas(models.Model):
    fecha = models.DateField()
    producto = models.CharField(max_length=100)
    cantidad = models.PositiveIntegerField()
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Venta {self.id} - {self.fecha}"

# Tabla de Comanda (Detalles de Venta)
class Comanda(models.Model):
    personal = models.ForeignKey(Personal, on_delete=models.CASCADE, related_name='comandas')
    venta = models.ForeignKey(Ventas, on_delete=models.CASCADE, related_name='comandas')
    producto = models.ForeignKey('Productos', on_delete=models.CASCADE, related_name='comandas')
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

# Tabla de Productos (Inventarios)
class Productos(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad_en_stock = models.PositiveIntegerField()
    categoria = models.ForeignKey('Categorias', on_delete=models.CASCADE, related_name='productos')

    def __str__(self):
        return self.nombre

# Tabla de Categorías
class Categorias(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre

# Tabla de Eventos
class Eventos(models.Model):
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=50)
    grupo = models.CharField(max_length=150)
    fecha = models.DateField()
    aforo = models.PositiveIntegerField()
    caso = models.ForeignKey('Casos', on_delete=models.SET_NULL, null=True, blank=True, related_name='eventos')
    cover = models.ForeignKey('Cover', on_delete=models.SET_NULL, null=True, blank=True, related_name='eventos')
    personal = models.ForeignKey(Personal, on_delete=models.SET_NULL, null=True, blank=True, related_name='eventos')

    def __str__(self):
        return self.nombre

# Tabla de Cover
class Cover(models.Model):
    precio = models.IntegerField()
    promo = models.CharField(max_length=30, blank=True)
    total = models.IntegerField()
    etario = models.CharField(max_length=30)

    def __str__(self):
        return f"Cover {self.id} - {self.precio}"

# Tabla de Inventario
class Inventario(models.Model):
    producto = models.ForeignKey(Productos, on_delete=models.CASCADE, related_name='inventarios')
    stock_actual = models.PositiveIntegerField()

# Tabla de Registro de Stock
class RegistroStock(models.Model):
    fecha = models.DateField()
    stock = models.JSONField()
    inventario = models.ForeignKey(Inventario, on_delete=models.CASCADE, related_name='registro_stock')

# Tabla de Compras
class Compras(models.Model):
    producto = models.ForeignKey(Productos, on_delete=models.CASCADE, related_name='compras')
    personal = models.ForeignKey(Personal, on_delete=models.SET_NULL, null=True, blank=True, related_name='compras')
    cantidad = models.PositiveIntegerField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)

# Tabla de Cuentas
class Cuentas(models.Model):
    fecha = models.DateField()
    consolidado = models.JSONField()
    ventas = models.ForeignKey(Ventas, on_delete=models.CASCADE, related_name='cuentas')

# Tabla de Pedidos
class Pedidos(models.Model):
    fecha = models.DateField()
    pedido = models.JSONField()
    compras = models.ForeignKey(Compras, on_delete=models.CASCADE, related_name='pedidos')

# Tabla de Casos
class Casos(models.Model):
    cuentas = models.ForeignKey(Cuentas, on_delete=models.CASCADE, related_name='casos')
    stock = models.ForeignKey(RegistroStock, on_delete=models.CASCADE, related_name='casos')
    pedido = models.ForeignKey(Pedidos, on_delete=models.CASCADE, related_name='casos')
    evento = models.ForeignKey(Eventos, on_delete=models.SET_NULL, null=True, blank=True, related_name='casos')
    performance = models.IntegerField()
    label1 = models.CharField(max_length=15)
    label2 = models.CharField(max_length=15)

    def __str__(self):
        return f"Caso {self.id} - Performance: {self.performance}"
