"""
Servicios de sincronización entre Ventas y Cuentas (Fase 2).

Fuente de verdad de "cuánto vendió" un mesero/barra: SesionTrabajo.total_ventas,
calculado en vivo desde las Comandas en estado 'entregada'.

EntregaPuntoVenta.total_talonario refleja ese valor automáticamente mientras
origen_talonario == 'sistema'. Si un administrador lo corrige a mano
(ej: hubo un bug y faltó una comanda), origen_talonario pasa a 'manual' y
la sincronización deja de tocar ese registro — la corrección manual manda.
"""
from decimal import Decimal


def sincronizar_entrega_sesion(sesion):
    """
    Crea o actualiza la EntregaPuntoVenta correspondiente a una SesionTrabajo
    cerrada, dentro del CierreDiario (en borrador) de su evento.

    No hace nada si:
    - la sesión no está cerrada,
    - no existe un CierreDiario en borrador para ese evento (aún no se creó,
      o ya se cerró y no debe tocarse más),
    - la entrega ya fue ajustada manualmente por un administrador.

    Retorna (entrega, actualizada) donde `actualizada` es True si se creó
    o si el total cambió. (None, False) si no se pudo sincronizar.
    """
    from .models import CierreDiario, EntregaPuntoVenta

    if sesion.estado != 'cerrada':
        return None, False

    cierre = CierreDiario.objects.filter(
        evento=sesion.evento,
        estado='borrador'
    ).first()
    if not cierre:
        return None, False

    entrega, created = EntregaPuntoVenta.objects.get_or_create(
        cierre=cierre,
        usuario=sesion.usuario,
        es_barra=sesion.es_barra,
        defaults={'total_talonario': sesion.total_ventas}
    )
    if created:
        return entrega, True

    if entrega.origen_talonario == 'manual':
        return entrega, False

    nuevo_total = sesion.total_ventas
    if entrega.total_talonario != nuevo_total:
        entrega.total_talonario = nuevo_total
        entrega.save(update_fields=['total_talonario'])
        return entrega, True

    return entrega, False


def sincronizar_ventas_cierre(cierre):
    """
    Sincroniza todas las sesiones cerradas del evento de este cierre.
    Se usa tanto automáticamente (al abrir detalle_cierre) como manualmente
    (botón "Sincronizar ventas") para cubrir el caso de sesiones cerradas
    antes de crear el CierreDiario, o comandas corregidas después del cierre
    de sesión.

    No hace nada si el cierre ya está 'cerrado' (no se tocan cifras de una
    noche ya cerrada) o si no tiene evento asignado.

    Retorna la cantidad de entregas creadas o actualizadas.
    """
    from ventas.models import SesionTrabajo

    if not cierre.evento or cierre.estado == 'cerrado':
        return 0

    sesiones = SesionTrabajo.objects.filter(
        evento=cierre.evento,
        estado='cerrada'
    ).select_related('usuario')

    total_actualizadas = 0
    for sesion in sesiones:
        _, actualizada = sincronizar_entrega_sesion(sesion)
        if actualizada:
            total_actualizadas += 1
    return total_actualizadas