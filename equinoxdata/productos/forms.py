from django import forms
from .models import ProductoBase, Receta, PresentacionProducto


from django import forms
from .models import PresentacionProducto

class PresentacionProductoForm(forms.ModelForm):
   class Meta:
        model = PresentacionProducto
        fields = '__all__'
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'producto_base': forms.Select(attrs={'class': 'form-control'}),
            'unidad_medida': forms.Select(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control'}),
            'precio_venta': forms.NumberInput(attrs={'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input ml-2'}),
        }


class ProductoBaseForm(forms.ModelForm):
    class Meta:
        model = ProductoBase
        fields = ['nombre', 'presentacion', 'categoria', 'medidas', 'cantidad']

    categoria = forms.BooleanField(required=False, label="¿Es insumo?", widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    medidas = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}), label="Medidas")

    def __init__(self, *args, **kwargs):
        super(ProductoBaseForm, self).__init__(*args, **kwargs)
        # Si el formulario ya tiene datos (se está editando), verifica si la categoría es insumo para mostrar el campo medidas
        if self.instance and self.instance.categoria:
            self.fields['medidas'].required = True  # Si es insumo, medidas debe ser requerido
        else:
            self.fields['medidas'].required = False  # Si no es insumo, medidas no es requerido



class RecetaForm(forms.ModelForm):
    class Meta:
        model = Receta
        fields = ['producto_final', 'insumo', 'cantidad']
        widgets = {
            'producto_final': forms.TextInput(attrs={'class': 'form-control'}),
            'insumo': forms.Select(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
insumo = forms.ModelChoiceField(queryset=ProductoBase.objects.all(), empty_label="Seleccione un insumo")




