# ventas/tasks.py
import logging
from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)

@shared_task
def enviar_confirmacion_pedido(pedido_id: int) -> dict:
    """Tarea que envía el correo de confirmación (W16 es placeholder)."""
    from ventas.models import Pedido
    
    try:
        pedido = Pedido.objects.select_related('cliente').get(pk=pedido_id)
    except Pedido.DoesNotExist:
        logger.error(f'Pedido {pedido_id} no existe.')
        return {'estado': 'error'}

    # W17 lo cambiará por un envío real de correo
    logger.info(f'[Tarea] Correo enviado a {pedido.cliente.correo} por el pedido {pedido.numero_pedido}')
    
    return {'estado': 'ok', 'pedido_id': pedido_id}

@shared_task
def verificar_stock_bajo(umbral: int = 5) -> dict:
    """Tarea que alerta sobre productos con stock bajo."""
    from productos.models import Producto
    
    bajos = list(Producto.objects.filter(activo=True, stock__lt=umbral).values('nombre', 'stock'))
    
    if bajos:
        logger.warning(f'[Tarea] Alerta: {len(bajos)} productos con stock bajo.')
    
    return {'total': len(bajos)}