# usuarios/urls.py
from django.urls import path
from .views import login_view, administrar_usuarios,inicio_view, administrar_usuarios, inicio_view
from django.contrib.auth import views as auth_views
from . import views

app_name = 'usuarios'  # Define el espacio de nombres para las URLs de esta app
urlpatterns = [
    path('login/', login_view, name='login'),
    path('administrar/', administrar_usuarios, name='administrar_usuarios'),
   
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('inicio/', inicio_view, name='inicio'),
    path('administrar/', administrar_usuarios, name='administrar_usuarios'),
    
    
    



  

]
