# catalogo/views.py
"""Vistas del catálogo, carrito y checkout con Stripe — W13/W14/W15."""

import stripe
from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView

from productos.models import Producto
from ventas.models import DetalleVenta, Pedido

from .filters import ProductoFilter
from .checkout_utils import (
    armar_items,
    calcular_totales,
    generar_numero_pedido,
    obtener_o_crear_cliente,
)

# Configurar la clave secreta de Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


# ── CATÁLOGO PÚBLICO (W13) ──────────────────────────────────────────────

class CatalogoView(ListView):
    model = Producto
    template_name = 'catalogo/catalogo.html'
    context_object_name = 'productos'
    paginate_by = 12

    def get_queryset(self):
        qs = Producto.objects.select_related('categoria').filter(activo=True).order_by('nombre')
        self.filtro = ProductoFilter(self.request.GET, queryset=qs)
        return self.filtro.qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['filtro'] = self.filtro
        return ctx


# ── CARRITO DE COMPRAS (W13) ────────────────────────────────────────────

def _obtener_carrito(request):
    return request.session.get('carrito', {})

def _guardar_carrito(request, carrito):
    request.session['carrito'] = carrito
    request.session.modified = True

def ver_carrito(request):
    carrito = _obtener_carrito(request)
    items = []
    total = Decimal('0.00')
    for prod_id, datos in carrito.items():
        precio = Decimal(datos['precio'])
        cantidad = int(datos['cantidad'])
        subtotal = precio * cantidad
        total += subtotal
        items.append({
            'prod_id': prod_id, 
            'nombre': datos['nombre'], 
            'precio': precio, 
            'cantidad': cantidad, 
            'subtotal': subtotal
        })
    return render(request, 'catalogo/carrito.html', {'items': items, 'total': total})

def agregar_al_carrito(request, producto_id):
    if request.method != 'POST':
        return redirect('catalogo:catalogo')
    producto = get_object_or_404(Producto, pk=producto_id, activo=True)
    carrito = _obtener_carrito(request)
    clave = str(producto_id)
    cantidad = int(request.POST.get('cantidad', 1))
    if clave in carrito:
        carrito[clave]['cantidad'] += cantidad
    else:
        carrito[clave] = {
            'nombre': producto.nombre, 
            'precio': str(producto.precio), 
            'cantidad': cantidad
        }
    _guardar_carrito(request, carrito)
    messages.success(request, f'"{producto.nombre}" agregado al carrito.')
    return redirect(request.META.get('HTTP_REFERER', 'catalogo:catalogo'))

def remover_del_carrito(request, producto_id):
    if request.method == 'POST':
        carrito = _obtener_carrito(request)
        carrito.pop(str(producto_id), None)
        _guardar_carrito(request, carrito)
        messages.warning(request, 'Producto eliminado del carrito.')
    return redirect('catalogo:carrito')

def actualizar_cantidad(request, producto_id):
    if request.method == 'POST':
        carrito = _obtener_carrito(request)
        clave = str(producto_id)
        cantidad = int(request.POST.get('cantidad', 1))
        if clave in carrito:
            if cantidad > 0:
                carrito[clave]['cantidad'] = cantidad
            else:
                carrito.pop(clave)
        _guardar_carrito(request, carrito)
    return redirect('catalogo:carrito')

def vaciar_carrito(request):
    if request.method == 'POST':
        _guardar_carrito(request, {})
        messages.info(request, 'Carrito vaciado.')
    return redirect('catalogo:carrito')


# ── CHECKOUT CON STRIPE (W14) ───────────────────────────────────────────

@login_required
def checkout(request):
    """Proceso de pago: muestra resumen y crea PaymentIntent de Stripe."""
    carrito = _obtener_carrito(request)
    if not carrito:
        messages.warning(request, 'Tu carrito está vacío.')
        return redirect('catalogo:catalogo')

    totales = calcular_totales(carrito)
    items = armar_items(carrito)
    publishable_key = settings.STRIPE_PUBLISHABLE_KEY

    if request.method == 'POST':
        try:
            # 1. Vincular usuario con Cliente del ERP
            cliente = obtener_o_crear_cliente(request.user)

            # 2. Crear el Pedido en estado "pendiente" (con snapshot)
            numero = generar_numero_pedido()
            snapshot = [
                {
                    'producto_id': int(prod_id),
                    'nombre':      datos['nombre'],
                    'cantidad':    int(datos['cantidad']),
                    'precio':      datos['precio'],
                }
                for prod_id, datos in carrito.items()
            ]

            pedido = Pedido.objects.create(
                numero_pedido=numero,
                cliente=cliente,
                estado='pendiente',
                total_pagado=totales['total'],
                items_snapshot=snapshot,
            )

            # 3. SIMULACIÓN DE STRIPE (Comentado para evitar error de API Key)
            # monto_centavos = int(totales['total'] * 100)
            # intent = stripe.PaymentIntent.create(
            #     amount=monto_centavos,
            #     currency='mxn',
            #     metadata={
            #         'pedido_id': pedido.pk,
            #         'pedido_num': pedido.numero_pedido,
            #         'cliente': cliente.nombre,
            #     },
            #     idempotency_key=f'pedido-{pedido.pk}',
            # )
            
            client_secret_falso = "pi_simulado_secret_123"

            # 4. Retornar client_secret al template
            return render(request, 'catalogo/checkout.html', {
                'carrito': carrito,
                'items': items,
                'totales': totales,
                'pedido': pedido,
                'client_secret': client_secret_falso,
                'publishable_key': publishable_key,
            })

        except stripe.error.StripeError as exc:
            messages.error(request, f'Error al conectar con Stripe: {exc.user_message}')
            return redirect('catalogo:pago_error')
        except Exception as exc:
            messages.error(request, f'Error inesperado en el pago: {exc}')
            return redirect('catalogo:pago_error')

    # GET — solo mostrar resumen (sin PaymentIntent)
    return render(request, 'catalogo/checkout.html', {
        'carrito': carrito,
        'items': items,
        'totales': totales,
        'client_secret': None,
        'publishable_key': publishable_key,
    })


# ── CONFIRMACIÓN DE PAGO (W15) ──────────────────────────────────────────

def pago_exitoso(request, pedido_id: int):
    """Vista de confirmación post-pago exitoso."""
    pedido = get_object_or_404(Pedido, pk=pedido_id)

    # Forzar el pago para el proyecto escolar
    if pedido.estado == 'pendiente':
        pedido.estado = 'pagado'
        pedido.save(update_fields=['estado'])

    # Vaciar el carrito al confirmar el pago
    _guardar_carrito(request, {})
    
    messages.success(
        request,
        f'¡Pago exitoso! Tu pedido {pedido.numero_pedido} está confirmado. Total: ${pedido.total_pagado}'
    )

    return render(request, 'catalogo/pago_exitoso.html', {'pedido': pedido})


def pago_error(request):
    """Vista de error de pago — muestra mensaje y permite reintentar."""
    return render(request, 'catalogo/pago_error.html')