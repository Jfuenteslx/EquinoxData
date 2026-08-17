from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import date
from .forms import LoginForm, UsuarioForm
from .models import Usuario
from eventos.models import Evento


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('usuarios:inicio')
        else:
            return render(request, 'usuarios/login.html', {
                'error': 'Usuario o contraseña incorrectos.'
            })
    return render(request, 'usuarios/login.html')

@login_required
def inicio_view(request):
    from datetime import date
    from ventas.models import SesionTrabajo
    from inventarios.models import Inventario
    from compras.models import Pedido
    from cuentas.models import CierreDiario

    hoy = date.today()

    # Eventos
    eventos_proximos = Evento.objects.filter(fecha__gte=hoy).order_by('fecha')[:3]
    eventos_pasados = Evento.objects.filter(fecha__lt=hoy).order_by('-fecha')[:6]

    # Sesiones activas hoy
    sesiones_activas = SesionTrabajo.objects.filter(
        estado='abierta',
        fecha_apertura__date=hoy
    ).select_related('usuario', 'evento')

    # Ventas del día
    total_ventas_hoy = sum(s.total_ventas for s in sesiones_activas)

    # Cierre diario de hoy
    cierre_hoy = CierreDiario.objects.filter(fecha=hoy).first()

    # Stock crítico (botellas <= 2)
    stock_critico = Inventario.objects.filter(
        botellas__lte=2,
        botellas__gte=0,
        producto__habilitado=True
    ).select_related('producto').order_by('botellas')[:5]

    # Pedidos activos
    pedidos_activos = Pedido.objects.filter(
        estado__in=['borrador', 'aprobado', 'en_proceso']
    ).order_by('-fecha_solicitud')[:5]

    return render(request, 'usuarios/dashboard.html', {
        'eventos_proximos': eventos_proximos,
        'eventos_pasados': eventos_pasados,
        'sesiones_activas': sesiones_activas,
        'total_ventas_hoy': total_ventas_hoy,
        'cierre_hoy': cierre_hoy,
        'stock_critico': stock_critico,
        'pedidos_activos': pedidos_activos,
        'hoy': hoy,
    })


@login_required
def administrar_usuarios(request):
    # Solo el administrador puede gestionar usuarios
    if not request.user.tiene_acceso_usuarios():
        messages.error(request, 'No tiene permisos para acceder a esta sección.')
        return redirect('usuarios:inicio')

    if request.method == 'POST':
        usuario_id = request.POST.get('usuario_id')

        # Editar usuario existente
        if usuario_id:
            usuario = get_object_or_404(Usuario, id=usuario_id)
            form = UsuarioForm(request.POST, instance=usuario)
            if form.is_valid():
                form.save()
                messages.success(request, f'Usuario {usuario.username} actualizado correctamente.')
            else:
                messages.error(request, 'Error al actualizar el usuario. Revise los datos.')

        # Crear nuevo usuario
        else:
            form = UsuarioForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Usuario creado correctamente.')
            else:
                messages.error(request, 'Error al crear el usuario. Revise los datos.')

        return redirect('usuarios:administrar_usuarios')

    usuarios = Usuario.objects.all().order_by('rol', 'username')
    form = UsuarioForm()
    return render(request, 'usuarios/administrar_usuarios.html', {
        'usuarios': usuarios,
        'form': form,
    })