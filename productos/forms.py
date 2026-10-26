from django import forms
from .models import Producto

class ProductoForm(forms.ModelForm):
    class Meta:
        model  = Producto
        fields = ['nombre', 'precio', 'stock', 'categoria', 'proveedor', 'activo']
        widgets = {
            'nombre':    forms.TextInput(attrs={'class': 'erp-input', 'placeholder': 'Nombre del producto'}),
            'precio':    forms.NumberInput(attrs={'class': 'erp-input', 'step': '0.01', 'min': '0'}),
            'stock':     forms.NumberInput(attrs={'class': 'erp-input', 'min': '0'}),
            'categoria': forms.Select(attrs={'class': 'erp-input'}),
            'proveedor': forms.Select(attrs={'class': 'erp-input'}),
        }
        labels = {
            'nombre': 'Nombre', 'precio': 'Precio ($)', 'stock': 'Stock disponible',
            'categoria': 'Categoría', 'proveedor': 'Proveedor', 'activo': 'Activo',
        }