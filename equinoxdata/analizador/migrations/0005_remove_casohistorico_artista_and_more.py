# Generated by Django 4.2 on 2024-11-26 03:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analizador', '0004_parametro'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='casohistorico',
            name='artista',
        ),
        migrations.RemoveField(
            model_name='casohistorico',
            name='eficacia',
        ),
        migrations.RemoveField(
            model_name='casohistorico',
            name='fecha_evento',
        ),
        migrations.RemoveField(
            model_name='casohistorico',
            name='nombre_evento',
        ),
        migrations.AddField(
            model_name='casohistorico',
            name='coeficiente',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='casohistorico',
            name='genero_musical',
            field=models.CharField(blank=True, default='Ninguna', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='casohistorico',
            name='performance',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='casohistorico',
            name='promociones',
            field=models.CharField(default='Ninguna', max_length=255),
        ),
        migrations.AddField(
            model_name='casohistorico',
            name='show_presentado',
            field=models.CharField(default='Ninguna', max_length=255),
        ),
        migrations.AddField(
            model_name='casohistorico',
            name='tipo_evento',
            field=models.CharField(default='Ninguna', max_length=255),
        ),
    ]
