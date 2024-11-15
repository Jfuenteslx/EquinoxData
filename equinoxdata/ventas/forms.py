from django import forms
from .models import Comanda, PresentacionProducto

class ComandaForm(forms.ModelForm):
    class Meta:
        model = Comanda
        fields = ['producto', 'cantidad']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Aquí puedes añadir algún campo adicional si es necesario, pero el formulario debe manejar PresentacionProducto
        self.fields['producto'].queryset = PresentacionProducto.objects.all()  # Solo PresentacionProducto
        self.fields['cantidad'].widget = forms.NumberInput(attrs={'min': 1})  # Asegurarse de que la cantidad sea un número positivo

    def clean_total(self):
        # Obtener la presentación del producto y la cantidad
        producto = self.cleaned_data['producto']
        cantidad = self.cleaned_data['cantidad']

        # Calcular el total
        total = producto.precio * cantidad
        return total
    # ventas/forms.py

from django import forms

class FiltroFechaForm(forms.Form):
    fecha = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True,
        label="Seleccionar fecha"
    )

    
