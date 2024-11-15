# usuarios/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Usuario

# Formulario de inicio de sesión
class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

# Formulario para crear un nuevo usuario
class UsuarioCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)  # Cambié 'correo' por 'email'

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'password1', 'password2']  # Cambié 'correo' por 'email'

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['username', 'first_name', 'last_name', 'rol', 'CI', 'is_active', 'is_staff']
        widgets = {
            'is_active': forms.CheckboxInput(),
            'is_staff': forms.CheckboxInput(),
        }

    def __init__(self, *args, **kwargs):
        super(UsuarioForm, self).__init__(*args, **kwargs)
        # Puedes personalizar los widgets, por ejemplo, cambiando el tipo de los campos booleanos
        self.fields['is_active'].widget.attrs.update({'class': 'form-check-input'})
        self.fields['is_staff'].widget.attrs.update({'class': 'form-check-input'})