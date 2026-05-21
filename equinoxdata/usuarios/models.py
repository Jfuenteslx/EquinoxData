from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils import timezone


class Usuario(AbstractUser):

    ROL_CHOICES = [
        ('administrador', 'Administrador'),
        ('jefe_barra', 'Jefe de Barra'),
        ('bartender', 'Bartender'),
        ('mesero', 'Mesero'),
    ]

    CI = models.CharField(max_length=20, unique=True, blank=True, null=True)
    rol = models.CharField(
        max_length=50,
        choices=ROL_CHOICES,
        blank=True,
        null=True
    )

    groups = models.ManyToManyField(
        Group,
        related_name='usuarios_user_set',
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='usuarios_user_set',
        blank=True,
    )

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return self.username

    def es_administrador(self):
        return self.rol == 'administrador'

    def es_jefe_barra(self):
        return self.rol == 'jefe_barra'

    def es_bartender(self):
        return self.rol == 'bartender'

    def es_mesero(self):
        return self.rol == 'mesero'

    def tiene_acceso_ventas(self):
        return self.rol in ['administrador', 'jefe_barra', 'bartender', 'mesero']

    def tiene_acceso_compras(self):
        return self.rol in ['administrador', 'jefe_barra']

    def tiene_acceso_inventarios(self):
        return self.rol in ['administrador', 'jefe_barra']

    def tiene_acceso_analizador(self):
        return self.rol in ['administrador', 'jefe_barra']

    def tiene_acceso_usuarios(self):
        return self.rol == 'administrador'


class Sesion(models.Model):
    marca = models.DateTimeField(default=timezone.now)
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='sesiones'
    )

    class Meta:
        verbose_name = 'Sesión'
        verbose_name_plural = 'Sesiones'

    def __str__(self):
        return f"Sesión de {self.usuario.first_name} {self.usuario.last_name} en {self.marca}"