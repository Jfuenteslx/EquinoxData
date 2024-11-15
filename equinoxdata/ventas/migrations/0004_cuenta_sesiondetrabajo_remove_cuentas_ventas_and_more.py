# Generated by Django 4.2 on 2024-11-14 06:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('productos', '0004_alter_presentacionproducto_tipo_presentacion'),
        ('ventas', '0003_alter_comanda_producto_alter_venta_producto'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cuenta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_venta', models.DecimalField(decimal_places=2, max_digits=10)),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('detalles_ventas', models.JSONField()),
            ],
        ),
        migrations.CreateModel(
            name='SesionDeTrabajo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_inicio', models.DateTimeField(auto_now_add=True)),
                ('fecha_fin', models.DateTimeField(blank=True, null=True)),
                ('estado', models.CharField(choices=[('abierta', 'Abierta'), ('cerrada', 'Cerrada')], default='abierta', max_length=10)),
                ('total_ventas', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
            ],
        ),
        migrations.RemoveField(
            model_name='cuentas',
            name='ventas',
        ),
        migrations.RenameField(
            model_name='comanda',
            old_name='precio_unitario',
            new_name='total',
        ),
        migrations.RenameField(
            model_name='comanda',
            old_name='personal',
            new_name='usuario',
        ),
        migrations.RemoveField(
            model_name='comanda',
            name='subtotal',
        ),
        migrations.RemoveField(
            model_name='comanda',
            name='venta',
        ),
        migrations.RemoveField(
            model_name='venta',
            name='cantidad',
        ),
        migrations.RemoveField(
            model_name='venta',
            name='producto',
        ),
        migrations.AddField(
            model_name='venta',
            name='comanda',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='ventas.comanda'),
        ),
        migrations.AlterField(
            model_name='comanda',
            name='producto',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='productos.productobase'),
        ),
        migrations.AlterField(
            model_name='venta',
            name='fecha',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]