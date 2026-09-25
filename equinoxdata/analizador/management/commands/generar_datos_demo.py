import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from eventos.models import Evento
from analizador.models import CasoHistorico
from analizador.inferencia import reglas_inferencia
from productos.models import ProductoBase

PREFIJO_DEMO = '[DEMO]'

BANDAS_HIST = [
    'Kranium Negro', 'Los Vertigos', 'Sonido Andino', 'Distorsion Sur',
    'Cielo de Plomo', 'Los Mecanicos', 'Ruido Blanco', 'La Yunta Brava',
]
BANDA_NUEVA_1 = 'Los Kjarkas Underground'
BANDA_NUEVA_2 = 'Sonora Altiplano'
BANDA_NUEVA_3 = 'Vertigo Nocturno'

TIPOS = ['Concierto', 'Fiesta', 'Stand up comedy', 'Evento especial']
GENEROS = [
    'Rock clasico', 'Rock alternativo', 'Punk', 'Electronica',
    'Metal', 'Pop Rock', 'Rap', 'Rock Latino', 'Ska / Murga',
]
PROMOS = [
    'Cumpleaneros del mes', 'Tequilazo', 'JagerNight', 'Fiesta Pacena',
    'Fiesta de disfraces', 'Drink de cortesia', 'No aplica',
]


class Command(BaseCommand):
    help = 'Genera (o limpia) datos sinteticos de demostracion para el analizador.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limpiar', action='store_true',
            help='Borra todos los eventos y casos historicos marcados como [DEMO].'
        )

    def handle(self, *args, **options):
        if options['limpiar']:
            eventos_demo = Evento.objects.filter(nombre__startswith=PREFIJO_DEMO)
            n = eventos_demo.count()
            eventos_demo.delete()
            self.stdout.write(self.style.SUCCESS(
                f'Se borraron {n} eventos [DEMO] (y sus casos historicos en cascada).'
            ))
            return

        productos = list(ProductoBase.objects.filter(habilitado=True))
        if not productos:
            self.stdout.write(self.style.ERROR(
                'No hay ProductoBase habilitados en la base. Cargá inventario antes de generar datos demo.'
            ))
            return

        hoy = timezone.now()

        # ------------------------------------------------------------
        # 1) Eventos FUTUROS (para elegir como "evento a analizar")
        # ------------------------------------------------------------
        eventos_futuros_config = [
            {
                'nombre': f'{PREFIJO_DEMO} Noche de Rock Alternativo',
                'banda': BANDA_NUEVA_1,
                'tipo_evento': 'Concierto',
                'genero_musical': 'Rock alternativo',
                'promociones': 'Tequilazo',
                'dias': 10,
            },
            {
                'nombre': f'{PREFIJO_DEMO} Fiesta Electronica',
                'banda': BANDA_NUEVA_2,
                'tipo_evento': 'Fiesta',
                'genero_musical': 'Electronica',
                'promociones': 'JagerNight',
                'dias': 17,
            },
            {
                'nombre': f'{PREFIJO_DEMO} Punk Underground',
                'banda': BANDA_NUEVA_3,
                'tipo_evento': 'Concierto',
                'genero_musical': 'Punk',
                'promociones': 'No aplica',
                'dias': 24,
            },
        ]

        eventos_futuros = []
        for cfg in eventos_futuros_config:
            ev, _ = Evento.objects.update_or_create(
                nombre=cfg['nombre'],
                defaults={
                    'banda': cfg['banda'],
                    'fecha': hoy + timedelta(days=cfg['dias']),
                    'descripcion': 'Evento de demostracion (no oficial) para probar el analizador.',
                }
            )
            eventos_futuros.append((ev, cfg))

        # ------------------------------------------------------------
        # 2) Eventos HISTORICOS + CasoHistorico (datos sinteticos)
        #    Cada uno se alinea a proposito con uno de los eventos
        #    futuros para que buscar_casos_similares() encuentre matches.
        # ------------------------------------------------------------
        historicos_config = []
        for cfg in eventos_futuros_config:
            # 3 casos "afines" (mismo tipo/genero/promo, banda distinta) por cada futuro
            for i in range(3):
                historicos_config.append({
                    'nombre': f"{PREFIJO_DEMO} {cfg['tipo_evento']} {cfg['genero_musical']} #{i+1}",
                    'banda': random.choice(BANDAS_HIST),
                    'tipo_evento': cfg['tipo_evento'],
                    'genero_musical': cfg['genero_musical'],
                    'promociones': cfg['promociones'] if random.random() > 0.3 else random.choice(PROMOS),
                    'dias_atras': random.randint(20, 300),
                })
        # un par de casos "ruido" que no matchean con nada, para mostrar que el
        # motor filtra por umbral y no muestra cualquier cosa
        for _ in range(2):
            historicos_config.append({
                'nombre': f'{PREFIJO_DEMO} Evento variado #{random.randint(100,999)}',
                'banda': random.choice(BANDAS_HIST),
                'tipo_evento': random.choice(TIPOS),
                'genero_musical': random.choice(GENEROS),
                'promociones': random.choice(PROMOS),
                'dias_atras': random.randint(300, 600),
            })

        creados = 0
        for cfg in historicos_config:
            ev, _ = Evento.objects.update_or_create(
                nombre=cfg['nombre'],
                defaults={
                    'banda': cfg['banda'],
                    'fecha': hoy - timedelta(days=cfg['dias_atras']),
                    'descripcion': 'Evento de demostracion (no oficial) para probar el analizador.',
                }
            )

            aforo = random.randint(60, 280)
            ventas_esperadas = random.randint(2000, 20000)
            consumo = random.randint(30, 200)

            coeficiente = reglas_inferencia(aforo, ventas_esperadas, consumo)

            # ventas reales simuladas +/-25% de lo esperado, para un performance realista
            ventas_reales = round(ventas_esperadas * random.uniform(0.75, 1.25), 2)
            performance = round((ventas_reales / ventas_esperadas) * 100, 2) if ventas_esperadas else 0

            # resumen de ventas por producto real del inventario, proporcional al aforo/consumo
            resumen_ventas = {}
            n_productos = min(len(productos), random.randint(4, 8))
            for prod in random.sample(productos, n_productos):
                cantidad = max(1, round((aforo * consumo / 1000) * random.uniform(0.3, 1.2)))
                precio_ref = float(prod.precio_costo) * 2.2 if prod.precio_costo else 15.0
                resumen_ventas[prod.nombre] = {
                    'cantidad_total': cantidad,
                    'total_bs': round(cantidad * precio_ref, 2),
                }

            resumen_inventario = {}
            for prod in productos:
                inv = getattr(prod, 'inventario', None)
                resumen_inventario[prod.nombre] = {
                    'botellas': inv.botellas if inv else 0,
                    'medidas_sueltas': float(inv.medidas_sueltas) if inv else 0.0,
                }

            CasoHistorico.objects.update_or_create(
                evento=ev,
                defaults={
                    'tipo_evento': cfg['tipo_evento'],
                    'genero_musical': cfg['genero_musical'],
                    'promociones': cfg['promociones'],
                    'aforo_esperado': aforo,
                    'ventas_esperadas': ventas_reales,
                    'consumo_per_capita': consumo,
                    'coeficiente': coeficiente,
                    'performance': performance,
                    'resumen_ventas': resumen_ventas,
                    'resumen_inventario': resumen_inventario,
                    'recomendacion_compra': {},
                }
            )
            creados += 1

        self.stdout.write(self.style.SUCCESS(
            f'Listo: {len(eventos_futuros)} eventos futuros [DEMO] creados para analizar, '
            f'{creados} casos historicos [DEMO] generados con el motor real.'
        ))
        self.stdout.write(self.style.WARNING(
            'Recordatorio: son datos SINTETICOS solo para la demo. Correr '
            '"python manage.py generar_datos_demo --limpiar" para borrarlos despues.'
        ))