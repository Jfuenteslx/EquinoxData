from django import forms
from eventos.models import Evento
from django.utils.timezone import now


TIPO_EVENTO_CHOICES = [
    ('', '— Seleccione —'),
    ('Concierto', 'Concierto'),
    ('Stand up comedy', 'Stand up comedy'),
    ('Fiesta', 'Fiesta'),
    ('Evento especial', 'Evento especial'),
]

GENERO_MUSICAL_CHOICES = [
    ('', '— Seleccione —'),
    ('Rock clasico', 'Rock clasico'),
    ('Rock alternativo', 'Rock alternativo'),
    ('Punk', 'Punk'),
    ('Electronica', 'Electronica'),
    ('Metal', 'Metal'),
    ('Pop Rock', 'Pop Rock'),
    ('Rap', 'Rap'),
    ('Rock Latino', 'Rock Latino'),
    ('Ska / Murga', 'Ska / Murga'),
    ('No aplica', 'No aplica'),
]

PROMOCIONES_CHOICES = [
    ('', '— Seleccione —'),
    ('Cumpleaneros del mes', 'Cumpleaneros del mes'),
    ('Tequilazo', 'Tequilazo'),
    ('JagerNight', 'JagerNight'),
    ('Fiesta Pacena', 'Fiesta Pacena'),
    ('Fiesta de disfraces', 'Fiesta de disfraces'),
    ('Drink de cortesia', 'Drink de cortesia'),
    ('No aplica', 'No aplica'),
]


class ParametrosForm(forms.Form):
    evento = forms.ModelChoiceField(
        queryset=Evento.objects.filter(fecha__gte=now().date()).order_by('fecha'),
        label='Evento a analizar',
        required=True,
        empty_label='— Seleccione un evento —',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    tipo_evento = forms.ChoiceField(
        choices=TIPO_EVENTO_CHOICES,
        label='Tipo de evento',
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    genero_musical = forms.ChoiceField(
        choices=GENERO_MUSICAL_CHOICES,
        label='Genero musical',
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    promociones = forms.ChoiceField(
        choices=PROMOCIONES_CHOICES,
        label='Promociones / Agregados',
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    aforo = forms.IntegerField(
        label='Aforo esperado (personas)',
        min_value=0,
        max_value=300,
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: 150'
        })
    )
    ventas = forms.IntegerField(
        label='Ventas esperadas (Bs.)',
        min_value=2000,
        max_value=20000,
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: 12000'
        })
    )
    consumo = forms.IntegerField(
        label='Consumo esperado por persona (Bs.)',
        min_value=30,
        max_value=200,
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: 80'
        })
    )

    def save(self):
        from .models import ParametrosEntrada
        data = self.cleaned_data
        return ParametrosEntrada.objects.create(
            evento=data['evento'],
            aforo_esperado=data['aforo'],
            ventas_esperadas=data['ventas'],
            consumo_esperado=data['consumo'],
            tipo_evento=data['tipo_evento'],
            genero_musical=data.get('genero_musical', ''),
            promociones=data.get('promociones', 'No aplica'),
        )


class BusquedaForm(forms.Form):
    tipo_evento = forms.ChoiceField(
        choices=TIPO_EVENTO_CHOICES,
        label='Tipo de evento',
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    genero_musical = forms.ChoiceField(
        choices=GENERO_MUSICAL_CHOICES,
        label='Genero musical',
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    promociones = forms.ChoiceField(
        choices=PROMOCIONES_CHOICES,
        label='Promociones',
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )