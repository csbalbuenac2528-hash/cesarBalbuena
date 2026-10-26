from django import forms
from .models import Cliente

class ClienteForm(forms.ModelForm):
    class Meta:
        model  = Cliente
        fields = ['nombre', 'correo', 'telefono', 'activo']
        widgets = {
            'nombre':   forms.TextInput(attrs={'class': 'erp-input', 'placeholder': 'Nombre completo'}),
            'correo':   forms.EmailInput(attrs={'class': 'erp-input', 'placeholder': 'correo@ejemplo.com'}),
            'telefono': forms.TextInput(attrs={'class': 'erp-input', 'placeholder': '461 123 4567'}),
        }