# catalogo/context_processors.py
"""Context processors de la app catalogo — W13.

Inyecta el contador del carrito en todos los templates.
"""

def carrito_info(request):
    """Calcula el total de items en el carrito.

    Se ejecuta en cada petición para que el contador del carrito
    esté disponible en la barra de navegación (base.html) sin
    necesidad de pasarlo manualmente en cada vista.

    Returns:
        dict: {'carrito_total_items': int}
    """
    carrito = request.session.get('carrito', {})
    total_items = sum(
        int(item.get('cantidad', 0)) for item in carrito.values()
    )
    return {'carrito_total_items': total_items}