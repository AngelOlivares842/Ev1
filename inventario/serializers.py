from django.contrib.auth.models import Group, User
from rest_framework import serializers
from .models import Producto, Cliente, Venta, VentaDetalle


class ProductoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Producto
        fields = [
            "url",
            "codigo",
            "nombre",
            "cantidad",
            "precio",
            "activo",
            "fecha_creacion"
        ]

class ClienteSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Cliente
        fields = [
            "url",
            "rut",
            "nombre",
            "email",
            "telefono",
            "es_habitual",
            "fecha_registro"
        ]

class VentaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Venta
        fields = [
            "url",
            "cliente_rut",
            "cliente_nombre",
            "total",
            "fecha_venta"
        ]

class VentaDetalleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = VentaDetalle
        fields = [
            "url",
            "venta",
            "producto",
            "cantidad_vendida",
            "precio_unitario",
            "subtotal"
        ]


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ["url", "username", "email", "groups"]


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ["url", "name"]