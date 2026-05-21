from django import forms
from .models import ProductoBase, ProductoMenu, RecetaItem


class ProductoBaseForm(forms.ModelForm):
    class Meta:
        model = ProductoBase
        fields = [
            'nombre', 'descripcion', 'unidad_medida',
            'contenido_neto_ml', 'medidas_por_unidad',
            'precio_costo', 'habilitado'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Fernet Branca'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Descripcion opcional'
            }),
            'unidad_medida': forms.Select(attrs={'class': 'form-control'}),
            'contenido_neto_ml': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 750'
            }),
            'medidas_por_unidad': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 16'
            }),
            'precio_costo': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Precio de costo en Bs.'
            }),
            'habilitado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'nombre': 'Nombre del insumo',
            'descripcion': 'Descripcion',
            'unidad_medida': 'Unidad de medida',
            'contenido_neto_ml': 'Contenido neto (ml)',
            'medidas_por_unidad': 'Medidas por botella/unidad',
            'precio_costo': 'Precio de costo (Bs.)',
            'habilitado': 'Habilitado',
        }

    def clean(self):
        cleaned_data = super().clean()
        unidad = cleaned_data.get('unidad_medida')
        contenido = cleaned_data.get('contenido_neto_ml')
        medidas = cleaned_data.get('medidas_por_unidad')

        if unidad == 'botella':
            if not contenido:
                self.add_error('contenido_neto_ml', 'Debe ingresar el contenido neto para botellas.')
            if not medidas or medidas <= 0:
                self.add_error('medidas_por_unidad', 'Debe ingresar la cantidad de medidas por botella.')
        return cleaned_data


class ProductoMenuForm(forms.ModelForm):
    class Meta:
        model = ProductoMenu
        fields = [
            'nombre', 'tipo', 'precio',
            'insumo_base', 'medidas_por_venta', 'habilitado'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Vaso de Fernet'
            }),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.50',
                'placeholder': 'Precio de venta en Bs.'
            }),
            'insumo_base': forms.Select(attrs={'class': 'form-control'}),
            'medidas_por_venta': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Medidas que descuenta al vender'
            }),
            'habilitado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'nombre': 'Nombre en el menu',
            'tipo': 'Tipo de producto',
            'precio': 'Precio de venta (Bs.)',
            'insumo_base': 'Insumo base',
            'medidas_por_venta': 'Medidas por venta',
            'habilitado': 'Disponible en menu',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['insumo_base'].queryset = ProductoBase.objects.filter(
            habilitado=True
        ).order_by('nombre')
        self.fields['insumo_base'].required = False
        self.fields['insumo_base'].empty_label = '— Sin insumo base (extras y cocteles) —'


class RecetaItemForm(forms.ModelForm):
    class Meta:
        model = RecetaItem
        fields = ['insumo', 'cantidad_medidas']
        widgets = {
            'insumo': forms.Select(attrs={'class': 'form-control'}),
            'cantidad_medidas': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.5',
                'min': '0.5',
                'placeholder': 'Ej: 4'
            }),
        }
        labels = {
            'insumo': 'Insumo',
            'cantidad_medidas': 'Cantidad de medidas',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['insumo'].queryset = ProductoBase.objects.filter(
            habilitado=True,
            unidad_medida='botella'
        ).order_by('nombre')


# Formset para manejar multiples items de receta
RecetaItemFormSet = forms.inlineformset_factory(
    ProductoMenu,
    RecetaItem,
    form=RecetaItemForm,
    extra=3,
    can_delete=True,
    min_num=1,
    validate_min=False,
)