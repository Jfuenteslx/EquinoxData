from django import forms
from .models import Evento, Parametro
from django.utils.timezone import now  # Importación correcta de 'now'

class ParametrosForm(forms.ModelForm):
    evento = forms.ModelChoiceField(
        queryset=Evento.objects.filter(fecha__gte=now()),  # Uso correcto de 'now()'
        label="Evento",
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control col-12',
        })
    )
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

    class Meta:
        model = Parametro
        fields = ['evento', 'aforo', 'ventas', 'consumo']


class BusquedaForm(forms.Form):
    # Buscar solo eventos que tengan una fecha mayor o igual a una fecha específica


    tipo_evento = forms.ChoiceField(
        choices=[
            ("Concierto", "Concierto"),
            ("Stand up comedy", "Stand up comedy"),
            ("Fiesta", "Fiesta"),
            ("Evento especial", "Evento especial"),
        ],
        label="Tipo de evento",
        required=False,
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
            ("Presentacion de discos", "Presentacion de discos"),
        ],
        label="Show presentado",
        required=False,
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
        required=False,
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
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control col-3',
        })
    )
