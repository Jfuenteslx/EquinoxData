# Generated by Django 4.2 on 2024-11-20 15:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventarios', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventario',
            name='saldo_bodega',
            field=models.IntegerField(default=0),
        ),
    ]
