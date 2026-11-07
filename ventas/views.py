# ventas/views.py
"""Vistas de la app ventas — W12 (CRUD, RBAC y generación de PDF)."""

import io
from decimal import Decimal, ROUND_HALF_UP

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.generic import DeleteView, DetailView, ListView

from xhtml2pdf import pisa

from .forms import DetalleVentaForm, VentaForm
from .models import DetalleVenta, Venta


# ── Vistas de Lectura (W07) ──────────────────────────────────────────────

class VentaListView(ListView):
    """Lista paginada de ventas en orden cronológico inverso."""
    model = Venta
    template_name = 'ventas/lista.html'
    context_object_name = 'ventas'
    paginate_by = 20

    def get_queryset(self):
        return Venta.objects.select_related('cliente').order_by('-fecha')


class VentaDetailView(DetailView):
    """Detalle de una venta con todas sus líneas de producto."""
    model = Venta
    template_name = 'ventas/detalle.html'
    context_object_name = 'venta'
    pk_url_kwarg = 'venta_id'

    def get_queryset(self):
        return Venta.objects.select_related('cliente').prefetch_related('detalles__producto')


# ── Vistas de Escritura (W08/W09) ────────────────────────────────────────

@login_required
@permission_required('ventas.add_venta', raise_exception=True)
def crear_venta(request):
    """Crea un encabezado de venta con una línea de detalle."""
    venta_form   = VentaForm(request.POST or None)
    detalle_form = DetalleVentaForm(request.POST or None)

    if request.method == 'POST':
        if venta_form.is_valid() and detalle_form.is_valid():
            venta = venta_form.save()
            detalle = detalle_form.save(commit=False)
            detalle.venta = venta
            detalle.save()
            
            messages.success(
                request, 
                f'Venta #{venta.pk} registrada. Total: ${venta.total:.2f}'
            )
            return redirect('ventas:detalle', venta_id=venta.pk)

    return render(request, 'ventas/crear.html', {
        'venta_form':   venta_form,
        'detalle_form': detalle_form,
    })


class VentaDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Confirmación y borrado de una venta (y sus detalles en cascada)."""
    model = Venta
    template_name = 'ventas/eliminar.html'
    pk_url_kwarg = 'venta_id'
    success_url = reverse_lazy('ventas:lista')
    permission_required = 'ventas.delete_venta'
    raise_exception = True

    def form_valid(self, form):
        pk = self.object.pk
        response = super().form_valid(form)
        messages.success(self.request, f'Venta #{pk} eliminada.')
        return response


# ── Generación de PDF (W12) ──────────────────────────────────────────────

@login_required
def venta_pdf(request, venta_id):
    """Genera y descarga la factura de una venta en formato PDF usando xhtml2pdf."""
    venta = get_object_or_404(
        Venta.objects.select_related("cliente").prefetch_related("detalles__producto"),
        pk=venta_id,
    )
    
    # Cálculo del IVA y total (Redondeo a 2 decimales)
    centavos = Decimal("0.01")
    subtotal = Decimal(venta.total).quantize(centavos, ROUND_HALF_UP)
    iva = (subtotal * Decimal("0.16")).quantize(centavos, ROUND_HALF_UP)
    
    context = {
        "venta": venta,
        "subtotal": subtotal,
        "iva": iva,
        "total_con_iva": subtotal + iva,
    }
    
    # Renderizar el HTML a un string
    html = render_to_string("ventas/factura_pdf.html", context)
    
    # Convertir el HTML a PDF usando xhtml2pdf
    result = io.BytesIO()
    pdf = pisa.CreatePDF(io.StringIO(html), dest=result)
    
    # Si no hay errores, devolver el PDF
    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="factura_{venta.pk}.pdf"'
        return response
        
    return HttpResponse("Error al generar el PDF", status=500)  