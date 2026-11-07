# productos/views.py
"""Vistas de la app productos — W12 (CRUD, imágenes y Excel)."""

import openpyxl

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)

from .forms import ProductoForm
from .models import Producto


# ── Vistas de Lectura (W07) ──────────────────────────────────────────────

class ProductoListView(ListView):
    model = Producto
    template_name = 'productos/lista.html'
    context_object_name = 'productos'
    paginate_by = 20

    def get_queryset(self):
        return Producto.objects.select_related('categoria', 'proveedor').filter(activo=True).order_by('nombre')


class ProductoDetailView(DetailView):
    model = Producto
    template_name = 'productos/detalle.html'
    context_object_name = 'producto'
    pk_url_kwarg = 'producto_id'

    def get_queryset(self):
        return Producto.objects.select_related('categoria', 'proveedor')


# ── Vistas de Escritura (W08/W09) ────────────────────────────────────────

class ProductoCreateView(LoginRequiredMixin, CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'productos/crear.html'
    success_url = reverse_lazy('productos:lista')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Producto "{self.object.nombre}" creado exitosamente.')
        return response


class ProductoUpdateView(LoginRequiredMixin, UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'productos/editar.html'
    pk_url_kwarg = 'producto_id'
    success_url = reverse_lazy('productos:lista')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Producto "{self.object.nombre}" actualizado.')
        return response


class ProductoDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Producto
    template_name = 'productos/eliminar.html'
    pk_url_kwarg = 'producto_id'
    success_url = reverse_lazy('productos:lista')
    permission_required = 'productos.delete_producto'
    raise_exception = True

    def form_valid(self, form):
        nombre = self.object.nombre
        response = super().form_valid(form)
        messages.success(self.request, f'Producto "{nombre}" eliminado.')
        return response


# ── Exportación a Excel (W12) ────────────────────────────────────────────

@login_required
def exportar_excel(request):
    """Exporta la lista de productos a un archivo Excel (.xlsx)."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Inventario"

    # Encabezados
    headers = ['ID', 'Nombre', 'Categoría', 'Precio', 'Stock', 'Activo']
    ws.append(headers)

    # Datos
    for prod in Producto.objects.select_related('categoria').all():
        ws.append([
            prod.pk, 
            prod.nombre, 
            prod.categoria.nombre, 
            float(prod.precio), 
            prod.stock, 
            "Sí" if prod.activo else "No"
        ])

    # Preparar la respuesta HTTP
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="inventario.xlsx"'
    wb.save(response)
    return response