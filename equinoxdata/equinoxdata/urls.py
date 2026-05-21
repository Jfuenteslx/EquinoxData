from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('usuarios:login')),
    path('usuarios/', include('usuarios.urls')),
    path('inventarios/', include('inventarios.urls')),
    path('productos/', include('productos.urls', namespace='productos')),
    path('compras/', include('compras.urls')),
    path('ventas/', include('ventas.urls')),
    path('eventos/', include('eventos.urls')),
    path('analizador/', include('analizador.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)