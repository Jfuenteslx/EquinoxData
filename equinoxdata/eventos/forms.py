from django import forms
from .models import Evento

class EventoForm(forms.ModelForm):
    class Meta:
        model = Evento
        fields = ['nombre', 'flyer', 'banda', 'fecha', 'descripcion', 'porcentaje_grupo', 'porcentaje_bar']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del evento'}),
            'flyer': forms.FileInput(attrs={'class': 'form-control'}),
            'banda': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Artista o banda'}),
            'fecha': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Descripción del evento'}),
            'porcentaje_grupo': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'porcentaje_bar': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Establecer etiquetas en negrita para todos los campos
        for field in self.fields.values():
            field.label = f'<span class="font-weight-bold">{field.label}</span>'