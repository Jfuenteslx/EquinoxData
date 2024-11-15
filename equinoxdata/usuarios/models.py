from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils import timezone


# Modelo de Usuario
class Usuario(AbstractUser):
    CI = models.CharField(max_length=20, unique=True, blank=True, null=True)  # Carnet de Identidad
    rol = models.CharField(max_length=50, blank=True, null=True)  # Ej: admin, cliente, vendedor

    # Personalización de nombres relacionados para permisos y grupos
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

    # Usar 'username' como nombre de usuario predeterminado
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []  # No se requieren campos adicionales

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return self.username

# Tabla de Sesiones
class Sesion(models.Model):
    marca = models.DateTimeField(default=timezone.now)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='sesiones')

    class Meta:
        verbose_name = 'Sesión'
        verbose_name_plural = 'Sesiones'

    def __str__(self):
        return f"Sesión de {self.usuario.first_name} {self.usuario.last_name} en {self.marca}"

