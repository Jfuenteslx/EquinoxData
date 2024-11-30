from django.utils.timezone import now
from datetime import date
# usuarios/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.urls import reverse
from .forms import LoginForm, UsuarioForm 
from .models import Usuario
from eventos.models import Evento




# Vista de login

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('usuarios:inicio')  # Asegúrate de que la redirección es a la vista 'inicio'
            else:
                form.add_error(None, 'Usuario o contraseña incorrectos.')
    else:
        form = LoginForm()

    return render(request, 'usuarios/login.html', {'form': form})

@login_required
def inicio_view(request):
    hoy = date.today()

    # Obtener los 3 próximos eventos
    eventos_proximos = Evento.objects.filter(fecha__gte=hoy).order_by('fecha')[:3]

    # Obtener los 3 eventos pasados
    eventos_pasados = Evento.objects.filter(fecha__lt=hoy).order_by('-fecha')[:6]

    # Pasar los eventos a la plantilla
    return render(request, 'usuarios/dashboard.html', {
        'eventos_proximos': eventos_proximos,
        'eventos_pasados': eventos_pasados
    })



# Vista para administrar usuarios



@login_required
def administrar_usuarios(request):
    if request.method == 'POST':
        # Crear un nuevo usuario
        if 'crear_usuario' in request.POST:
            form = UsuarioForm(request.POST)
            if form.is_valid():
                usuario = form.save(commit=False)  # No guardes todavía
                if request.POST.get('password'):
                    usuario.set_password(request.POST['password'])  # Encripta la contraseña
                usuario.save()  # Ahora guarda el usuario con la contraseña encriptada
                return redirect('usuarios:administrar_usuarios')
        
        # Editar un usuario existente
        elif 'editar_usuario' in request.POST:
            usuario_id = request.POST.get('usuario_id')
            usuario = Usuario.objects.get(id=usuario_id)
            usuario.username = request.POST['username']
            usuario.first_name = request.POST['first_name']
            usuario.last_name = request.POST['last_name']
            usuario.rol = request.POST['rol']
            usuario.CI = request.POST['CI']
            if request.POST.get('password'):
                usuario.set_password(request.POST['password'])  # Encripta la nueva contraseña
            usuario.save()
            return redirect('usuarios:administrar_usuarios')

    usuarios = Usuario.objects.all()  # Lista de todos los usuarios
    return render(request, 'usuarios/administrar_usuarios.html', {'usuarios': usuarios})
