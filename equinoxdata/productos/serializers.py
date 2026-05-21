from rest_framework import serializers
from .models import ProductoBase, PresentacionProducto, ProductoMenu, DetalleProductoMenu

class PresentacionProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PresentacionProducto
        fields = '__all__'

class ProductoBaseSerializer(serializers.ModelSerializer):
    presentaciones = PresentacionProductoSerializer(many=True, read_only=True)

    class Meta:
        model = ProductoBase
        fields = ['id', 'nombre', 'descripcion', 'unidad_medida', 'presentaciones']

class DetalleProductoMenuSerializer(serializers.ModelSerializer):
    producto_base = serializers.StringRelatedField()
    
    class Meta:
        model = DetalleProductoMenu
        fields = ['producto_base', 'cantidad']

class ProductoMenuSerializer(serializers.ModelSerializer):
    ingredientes = DetalleProductoMenuSerializer(source='detalleproductomenu_set', many=True, read_only=True)

    class Meta:
        model = ProductoMenu
        fields = ['id', 'nombre', 'precio', 'ingredientes']
