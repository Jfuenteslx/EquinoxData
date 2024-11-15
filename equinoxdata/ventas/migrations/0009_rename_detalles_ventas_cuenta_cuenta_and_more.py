# Generated by Django 4.2 on 2024-11-15 08:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ventas', '0008_venta_total'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cuenta',
            old_name='detalles_ventas',
            new_name='cuenta',
        ),
        migrations.RemoveField(
            model_name='cuenta',
            name='sesion_de_trabajo',
        ),
        migrations.RemoveField(
            model_name='cuenta',
            name='total_venta',
        ),
        migrations.AlterField(
            model_name='cuenta',
            name='fecha',
            field=models.DateField(unique=True),
        ),
    ]
