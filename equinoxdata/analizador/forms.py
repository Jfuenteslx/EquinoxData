from django import forms
from .models import Parametro, Evento

class ParametrosForm(forms.ModelForm):
    # Nuevos campos con widgets personalizados
    evento = forms.ModelChoiceField(
        queryset=Evento.objects.filter(fecha__gte="2024-11-01"),
        label="Evento",
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control',
        })
    )
    # Campos existentes con widgets de Bootstrap
    aforo = forms.IntegerField(
        label="Aforo esperado",
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'form-control col-3',
            'placeholder': 'Ingrese el aforo esperado',
        })
    )
    ventas = forms.IntegerField(
        label="Ventas esperadas",
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'form-control col-3',
            'placeholder': 'Ingrese las ventas esperadas',
        })
    )
    consumo = forms.IntegerField(
        label="Consumo esperado por cliente",
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'form-control col-3',
            'placeholder': 'Ingrese el consumo esperado por cliente',
        })
    )

    tipo_evento = forms.ChoiceField(
        choices=[
            ("Concierto", "Concierto"),
            ("Stand up comedy", "Stand up comedy"),
            ("Fiesta", "Fiesta"),
            ("Evento especial", "Evento especial"),
        ],
        label="Tipo de evento",
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control col-3',
        })
    )
    show_presentado = forms.ChoiceField(
        choices=[
            ("Rock Nacional", "Rock Nacional"),
            ("Tributo a un artista/ banda legendaria", "Tributo a un artista/ banda legendaria"),
            ("Especial genero musical", "Especial genero musical"),
            ("Especial decada o rango generacional", "Especial decada o rango generacional"),
            ("After Party", "After Party"),
            ("Artista Internacional o Extranjero", "Artista Internacional o Extranjero"),
            ("Fiesta tematica", "Fiesta tematica"),
        ],
        label="Show presentado",
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control col-3',
        })
    )
    genero_musical = forms.ChoiceField(
        choices=[
            ("Rock clasico", "Rock clasico"),
            ("Rock alternativo", "Rock alternativo"),
            ("Punk", "Punk"),
            ("Electronica", "Electronica"),
            ("Metal", "Metal"),
            ("Pop Rock", "Pop Rock"),
            ("Rap", "Rap"),
            ("Rock Latino", "Rock Latino"),
            ("Ska / Murga", "Ska / Murga"),
            ("No aplica", "No aplica"),
        ],
        label="Género musical",
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control col-3',
        })
    )
    promociones = forms.ChoiceField(
        choices=[
            ("Cumpleañeros del mes", "Cumpleañeros del mes"),
            ("Tequilazo", "Tequilazo"),
            ("JagerNight", "JagerNight"),
            ("Fiesta Paceña", "Fiesta Paceña"),
            ("Fiesta de disfraces", "Fiesta de disfraces"),
            ("Drink de cortesia", "Drink de cortesia"),
            ("No aplica", "No aplica"),
        ],
        label="Promociones / Agregados",
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control col-3',
        })
    )

    class Meta:
        model = Parametro
        fields = [
            'evento', 'aforo', 'ventas', 'consumo', 
            'tipo_evento', 'show_presentado', 'genero_musical', 'promociones'
        ]
