# usuarios/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.urls import reverse
from .forms import LoginForm, UsuarioForm 
from .models import Usuario




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

# Vista del dashboard o inicio
@login_required
# @user_passes_test(lambda u: u.is_staff)  # Asegura que solo los staff puedan acceder
def inicio_view(request):
    return render(request, 'usuarios/dashboard.html')





# Vista para administrar usuarios

@login_required
def administrar_usuarios(request):
    if request.method == 'POST':
        # Aquí deberías verificar si se está creando un nuevo usuario
        if 'crear_usuario' in request.POST:
            # Crear un nuevo usuario
            form = UsuarioForm(request.POST)
            if form.is_valid():
                form.save()  # Guarda el nuevo usuario en la base de datos
                return redirect('usuarios:administrar_usuarios')
        # Aquí puedes manejar la edición de un usuario
        elif 'editar_usuario' in request.POST:
            usuario_id = request.POST.get('usuario_id')
            usuario = Usuario.objects.get(id=usuario_id)
            usuario.username = request.POST['username']
            usuario.first_name = request.POST['first_name']
            usuario.last_name = request.POST['last_name']
            usuario.rol = request.POST['rol']
            usuario.CI = request.POST['CI']
            if request.POST.get('password'):
                usuario.set_password(request.POST['password'])
            usuario.save()
            return redirect('usuarios:administrar_usuarios')

    usuarios = Usuario.objects.all()  # O cualquier filtro que necesites
    return render(request, 'usuarios/administrar_usuarios.html', {'usuarios': usuarios})