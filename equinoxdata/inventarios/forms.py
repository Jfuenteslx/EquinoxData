from django import forms
from .models import Inventario, AperturaDiaria
from productos.models import ProductoBase


class AperturaDiariaForm(forms.Form):
    """
    Formulario dinámico para registrar el conteo físico de todos los insumos
    en una sola pantalla tipo hoja de cálculo.
    """
    def __init__(self, *args, **kwargs):
        productos = kwargs.pop('productos', None)
        super().__init__(*args, **kwargs)

        if productos:
            for producto in productos:
                self.fields[f'botellas_{producto.id}'] = forms.IntegerField(
                    min_value=0,
                    initial=0,
                    required=False,
                    widget=forms.NumberInput(attrs={
                        'class': 'form-control form-control-sm text-center',
                        'style': 'width: 80px;',
                        'min': '0',
                    })
                )
                self.fields[f'medidas_{producto.id}'] = forms.DecimalField(
                    min_value=0,
                    initial=0,
                    required=False,
                    decimal_places=1,
                    widget=forms.NumberInput(attrs={
                        'class': 'form-control form-control-sm text-center',
                        'style': 'width: 80px;',
                        'min': '0',
                        'step': '0.5',
                    })
                )


class AjusteInventarioForm(forms.ModelForm):
    """Formulario para ajuste manual de inventario."""
    class Meta:
        model = Inventario
        fields = ['botellas', 'medidas_sueltas']
        widgets = {
            'botellas': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'medidas_sueltas': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.5'
            }),
        }
        labels = {
            'botellas': 'Botellas',
            'medidas_sueltas': 'Medidas sueltas',
        }