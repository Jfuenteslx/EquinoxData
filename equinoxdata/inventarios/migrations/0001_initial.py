# Generated by Django 4.2 on 2024-11-20 04:06

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('productos', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RegistroStock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField(auto_now_add=True)),
                ('inventario_json', models.JSONField()),
            ],
        ),
        migrations.CreateModel(
            name='Saldo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.IntegerField()),
                ('medida', models.CharField(max_length=100)),
                ('fecha', models.DateField(default=django.utils.timezone.now)),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='productos.productobase')),
            ],
            options={
                'ordering': ['-fecha'],
            },
        ),
        migrations.CreateModel(
            name='Inventario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('saldo_bodega', models.IntegerField()),
                ('medidas_restantes', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('fecha_ingreso', models.DateTimeField(auto_now_add=True)),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='productos.productobase')),
            ],
        ),
    ]
