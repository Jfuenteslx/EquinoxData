
from django import forms
from productos.models import ProductoBase  # Importa el modelo ProductoBase
from .models import Inventario, RegistroStock  # Asegúrate de importar RegistroStock

class InventarioForm(forms.ModelForm):
    class Meta:
        model = Inventario
        fields = ['producto', 'stock_actual']  # Asegúrate de que 'producto' esté bien configurado con ProductoBase

class RegistrarStockForm(forms.ModelForm):
    class Meta:
        model = RegistroStock  # Ahora debería reconocer RegistroStock correctamente
        fields = ['fecha', 'stock', 'inventario']
        exclude = ['fecha']  # Si no quieres que 'fecha' sea editable, lo excluyes
