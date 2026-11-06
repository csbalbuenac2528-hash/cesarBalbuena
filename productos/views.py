# productos/views.py
"""Vistas de la app productos — W11 (con soporte para imágenes)."""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
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


# ── Vistas de Escritura (W08 / W09 / W11) ────────────────────────────────

class ProductoCreateView(LoginRequiredMixin, CreateView):
    model         = Producto
    form_class    = ProductoForm      # <-- ESTO ES LO IMPORTANTE
    template_name = 'productos/crear.html'
    success_url   = reverse_lazy('productos:lista')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Producto "{self.object.nombre}" creado exitosamente.')
        return response


class ProductoUpdateView(LoginRequiredMixin, UpdateView):
    model         = Producto
    form_class    = ProductoForm      # <-- ESTO ES LO IMPORTANTE
    template_name = 'productos/editar.html'
    pk_url_kwarg  = 'producto_id'
    success_url   = reverse_lazy('productos:lista')

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