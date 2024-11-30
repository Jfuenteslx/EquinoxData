from django import forms
from .models import Evento, Cover

class EventoForm(forms.ModelForm):
    class Meta:
        model = Evento
        fields = ['nombre', 'flyer', 'banda', 'fecha', 'descripcion', 'cover']  # Campos actualizados
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del evento'}),
            'flyer': forms.FileInput(attrs={'class': 'form-control'}),
            'banda': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Artista o banda'}),
            'fecha': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Descripción del evento'}),
            'cover': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Establecer etiquetas en negrita para todos los campos
        for field in self.fields.values():
            field.label = f'<span class="font-weight-bold">{field.label}</span>'



class CoverForm(forms.ModelForm):
    class Meta:
        model = Cover
        fields = ['precio', 'promo', 'total_asistentes', 'grupo_etario']
        widgets = {
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Ingrese el precio del cover'}),
            'promo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese la promoción (opcional)'}),
            'total_asistentes': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el número de asistentes'}),
            'grupo_etario': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el grupo etario (opcional)'}),
            'evento': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_precio(self):
        precio = self.cleaned_data.get('precio')
        if precio < 0:
            raise forms.ValidationError("El precio no puede ser negativo.")
        return precio

    def clean_total_asistentes(self):
        total_asistentes = self.cleaned_data.get('total_asistentes')
        if total_asistentes < 0:
            raise forms.ValidationError("El número de asistentes no puede ser negativo.")
        return total_asistentes

