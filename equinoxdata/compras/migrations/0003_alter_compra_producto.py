# Generated by Django 4.2 on 2024-11-13 08:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('productos', '0002_presentacionproducto_productobase_receta_and_more'),
        ('compras', '0002_alter_compra_producto'),
    ]

    operations = [
        migrations.AlterField(
            model_name='compra',
            name='producto',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='productos.productobase'),
        ),
    ]
