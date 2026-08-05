from django import forms
from .models import Comanda, ItemComanda
from productos.models import ProductoMenu


class ComandaForm(forms.ModelForm):
    class Meta:
        model = Comanda
        fields = ['referencia']
        widgets = {
            'referencia': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Mesa 3, Cumpleañero... (opcional)'
            }),
        }


class ItemComandaForm(forms.ModelForm):
    class Meta:
        model = ItemComanda
        fields = ['producto', 'cantidad']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['producto'].queryset = ProductoMenu.objects.filter(habilitado=True).order_by('tipo', 'nombre')
        self.fields['producto'].label = 'Producto'
        self.fields['cantidad'].label = 'Cantidad'