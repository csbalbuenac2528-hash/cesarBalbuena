# core/views.py

"""Vistas principales del proyecto ERP — W07.

Migración de HttpResponse → render() con templates y contexto.

"""

from django.shortcuts import render
from django.urls import reverse

def bienvenida(request):
    """Página de inicio del ERP con tarjetas de módulos.

    Context:
        modulos (list): Lista de dicts con icono, nombre, url y descripcion.

    Returns:
        HttpResponse con template bienvenida.html.

    """
    modulos = [
        {
            'nombre': 'Productos',
            'icono': '📦',
            'url': reverse('productos:lista'),     # Actualizado a 'lista' en W07
            'descripcion': 'Inventario, precios y stock',
        },
        {
            'nombre': 'Clientes',
            'icono': '👥',
            'url': reverse('clientes:lista'),      # Actualizado a 'lista' en W07
            'descripcion': 'Cartera y gestión de clientes',
        },
        {
            'nombre': 'Proveedores',
            'icono': '🏭',
            'url': reverse('proveedores:lista'),   # Actualizado a 'lista' en W07
            'descripcion': 'Red de proveedores',
        },
        {
            'nombre': 'Ventas',
            'icono': '💰',
            'url': reverse('ventas:lista'),        # Actualizado a 'lista' en W07
            'descripcion': 'Pedidos, facturas y cobros',
        },
        {
            'nombre': 'Reportes',
            'icono': '📊',
            'url': reverse('reportes:inicio'),     # Reportes se queda con 'inicio' hasta su semana
            'descripcion': 'Dashboard y analítica',
        },
        {
            'nombre': 'Admin',
            'icono': '⚙️',
            'url': '/admin/',
            'descripcion': 'Panel de administración Django',
        },
    ]
    
    return render(request, 'bienvenida.html', {'modulos': modulos})