
# usuarios/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .forms import LoginForm, UsuarioCreationForm, UsuarioChangeForm
from .models import Usuario, Personal
from django.db.models import Max

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
# @login_required
# @user_passes_test(lambda u: u.is_staff)
# def administrar_usuarios(request):
#     usuarios = Usuario.objects.all()

#     if request.method == 'POST':
#         if 'crear_usuario' in request.POST:
#             form = UsuarioCreationForm(request.POST)
#             if form.is_valid():
#                 form.save()
#                 messages.success(request, 'Usuario creado exitosamente.')
#                 return redirect('administrar_usuarios')

#         elif 'editar_usuario' in request.POST:
#             usuario = get_object_or_404(Usuario, id=request.POST.get("usuario_id"))
#             form = UsuarioChangeForm(request.POST, instance=usuario)
#             if form.is_valid():
#                 form.save()
#                 messages.success(request, 'Usuario editado exitosamente.')
#                 return redirect('administrar_usuarios')

#         elif 'eliminar_usuario' in request.POST:
#             usuario = get_object_or_404(Usuario, id=request.POST.get("usuario_id"))
#             usuario.delete()
#             messages.success(request, 'Usuario eliminado exitosamente.')
#             return redirect('administrar_usuarios')

#     context = {
#         'usuarios': usuarios,
#         'crear_form': UsuarioCreationForm(),
#         'editar_form': UsuarioChangeForm(),
#     }
#     return render(request, 'usuarios/administrar_usuarios.html', context)


from django.db.models import Max  # Para obtener la última marca de cada usuario

@login_required
@user_passes_test(lambda u: u.is_staff)
def administrar_usuarios(request):
    # Recuperar los usuarios y unimos con detalles del personal y última sesión
    usuarios_data = Usuario.objects.select_related('personal').annotate(
        ultima_sesion=Max('personal__sesion__marca')
    ).values(
        'id', 'correo', 'personal__nombre', 'personal__apellido', 
        'personal__CI', 'personal__rol', 'ultima_sesion'
    )

    if request.method == 'POST':
        if 'crear_usuario' in request.POST:
            form = UsuarioCreationForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Usuario creado exitosamente.')
                return redirect('administrar_usuarios')

        elif 'editar_usuario' in request.POST:
            usuario = get_object_or_404(Usuario, id=request.POST.get("usuario_id"))
            form = UsuarioChangeForm(request.POST, instance=usuario)
            if form.is_valid():
                form.save()
                messages.success(request, 'Usuario editado exitosamente.')
                return redirect('administrar_usuarios')

        elif 'eliminar_usuario' in request.POST:
            usuario = get_object_or_404(Usuario, id=request.POST.get("usuario_id"))
            usuario.delete()
            messages.success(request, 'Usuario eliminado exitosamente.')
            return redirect('administrar_usuarios')

    context = {
        'usuarios_data': usuarios_data,
        'crear_form': UsuarioCreationForm(),
        'editar_form': UsuarioChangeForm(),
    }
    return render(request, 'usuarios/administrar_usuarios.html', context)
