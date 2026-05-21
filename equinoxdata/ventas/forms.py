from django import forms
from .models import Comanda
from productos.models import ProductoMenu


class ComandaForm(forms.ModelForm):
    class Meta:
        model = Comanda
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
        self.fields['producto'].queryset = ProductoMenu.objects.filter(habilitado=True)
        self.fields['producto'].label = 'Producto'
        self.fields['cantidad'].label = 'Cantidad'