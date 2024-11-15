# Generated by Django 4.2 on 2024-11-14 06:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('analizador', '0002_alter_caso_cuentas'),
        ('ventas', '0004_cuenta_sesiondetrabajo_remove_cuentas_ventas_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.DeleteModel(
            name='Cuentas',
        ),
        migrations.AddField(
            model_name='sesiondetrabajo',
            name='usuario_encargado',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='cuenta',
            name='sesion_de_trabajo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cuentas', to='ventas.sesiondetrabajo'),
        ),
        migrations.AddField(
            model_name='comanda',
            name='sesion_de_trabajo',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='comandas', to='ventas.sesiondetrabajo'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='venta',
            name='sesion_de_trabajo',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='ventas', to='ventas.sesiondetrabajo'),
            preserve_default=False,
        ),
    ]
