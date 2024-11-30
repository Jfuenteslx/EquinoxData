from django import forms
from .models import Saldo

class SaldoForm(forms.ModelForm):
    class Meta:
        model = Saldo
        fields = ['producto', 'cantidad', 'medida', 'fecha']  # Asegúrate de incluir 'fecha'

    def __init__(self, *args, **kwargs):
        super(SaldoForm, self).__init__(*args, **kwargs)
        # Hacer que el campo 'fecha' sea solo lectura (visible pero no editable)
        self.fields['fecha'].widget = forms.DateInput(attrs={'readonly': 'readonly', 'class': 'form-control'})
