# usuarios/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario, Personal

# Formulario de inicio de sesión
class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

# Formulario para crear un nuevo usuario
class UsuarioCreationForm(UserCreationForm):
    correo = forms.EmailField(required=True)

    class Meta:
        model = Usuario
        fields = ['username', 'correo', 'password1', 'password2']

# Formulario para editar un usuario
class UsuarioChangeForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['username', 'correo', 'is_active', 'is_staff']
