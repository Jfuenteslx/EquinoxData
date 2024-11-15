from django import forms
from .models import ProductoBase
from .models import PresentacionProducto
from .models import Receta

class ProductoBaseForm(forms.ModelForm):
    class Meta:
        model = ProductoBase
        fields = ['nombre', 'medidas', 'stock_botellas']


class PresentacionProductoForm(forms.ModelForm):
    class Meta:
        model = PresentacionProducto
        fields = ['producto', 'nombre_presentacion', 'tipo_presentacion', 'consumo_por_presentacion_medidas', 'precio', 'es_ingrediente']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-control'}),
            'nombre_presentacion': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_presentacion': forms.Select(attrs={'class': 'form-control'}),
            'consumo_por_presentacion_medidas': forms.NumberInput(attrs={'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control'}),
            'es_ingrediente': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        

class RecetaForm(forms.ModelForm):
    class Meta:
        model = Receta
        fields = ['presentacion', 'ingrediente', 'cantidad_medidas']

        widgets = {
            'presentacion': forms.Select(attrs={'class': 'form-control'}),
            'ingrediente': forms.Select(attrs={'class': 'form-control'}),
            'cantidad_medidas': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }