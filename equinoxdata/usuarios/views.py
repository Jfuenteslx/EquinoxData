

# Create your views here.
# usuarios/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .forms import LoginForm, UsuarioCreationForm, UsuarioChangeForm
from .models import Usuario, Personal

# Vista de login

from django.shortcuts import render, redirect
from .forms import LoginForm  # Asegúrate de que importas el formulario correcto


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)  # Elimina el argumento 'request'
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')  # Redirigir al dashboard
            else:
                form.add_error(None, 'Usuario o contraseña incorrectos.')
    else:
        form = LoginForm()

    return render(request, 'usuarios/login.html', {'form': form})



# Vista para administrar usuarios
@login_required
@user_passes_test(lambda u: u.is_staff)  # Solo los usuarios con permiso de staff pueden acceder
def administrar_usuarios(request):
    usuarios = Usuario.objects.all()
    return render(request, 'usuarios/administrar_usuarios.html', {'usuarios': usuarios})

# Vista para crear un nuevo usuario
@login_required
@user_passes_test(lambda u: u.is_staff)
def crear_usuario(request):
    if request.method == 'POST':
        form = UsuarioCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario creado exitosamente.')
            return redirect('administrar_usuarios')  # Cambia 'administrar_usuarios' por tu vista correspondiente
    else:
        form = UsuarioCreationForm()
    return render(request, 'usuarios/crear_usuario.html', {'form': form})

# Vista para editar un usuario
@login_required
@user_passes_test(lambda u: u.is_staff)
def editar_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    if request.method == 'POST':
        form = UsuarioChangeForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario editado exitosamente.')
            return redirect('administrar_usuarios')  # Cambia 'administrar_usuarios' por tu vista correspondiente
    else:
        form = UsuarioChangeForm(instance=usuario)
    return render(request, 'usuarios/editar_usuario.html', {'form': form})

# Vista para eliminar un usuario
@login_required
@user_passes_test(lambda u: u.is_staff)
def eliminar_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    if request.method == 'POST':
        usuario.delete()
        messages.success(request, 'Usuario eliminado exitosamente.')
        return redirect('administrar_usuarios')  # Cambia 'administrar_usuarios' por tu vista correspondiente
    return render(request, 'usuarios/eliminar_usuario.html', {'usuario': usuario})

#aca se abre el dashboard

@login_required
def dashboard_view(request):
    return render(request, 'usuarios/dashboard.html')  # Crearás este archivo más adelante




# esta parte solo es para la demo

# views.py
from django.shortcuts import render

def inicio_view(request):
    return render(request, 'usuarios/dashboard.html')

def nueva_venta_view(request):
    return render(request, 'ventas/nueva_venta.html')

def editar_comanda_view(request):
    return render(request, 'ventas/editar_comanda.html')

def reportes_ventas_view(request):
    return render(request, 'ventas/reportes.html')

def consolidar_view(request):
    return render(request, 'ventas/consolidar.html')

def pedidos_view(request):
    return render(request, 'pedidos.html')

def registrar_compras_view(request):
    return render(request, 'inventario/registrar_compras.html')

def registrar_saldos_view(request):
    return render(request, 'inventario/registrar_saldos.html')

def productos_view(request):
    return render(request, 'inventario/productos.html')

def reportes_inventario_view(request):
    return render(request, 'inventario/reportes.html')

def administrar_eventos_view(request):
    return render(request, 'agenda/administrar_eventos.html')

def consultar_casos_view(request):
    return render(request, 'reportes/consultar_casos.html')

def analizar_eventos_view(request):
    return render(request, 'reportes/analizar_eventos.html')

def personal_view(request):
    return render(request, 'personal.html')
