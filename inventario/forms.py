from django import forms
from .models import Producto, Cliente, Venta

class ProductoForm(forms.ModelForm):
    """Formulario para crear y editar productos"""
    class Meta:
        model = Producto
        fields = ['codigo', 'nombre', 'cantidad', 'precio']  # Campos del modelo a incluir
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),  # Validación: no negativo
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),  # Decimales
        }

class ClienteForm(forms.ModelForm):
    """Formulario para registrar clientes"""
    class Meta:
        model = Cliente
        fields = ['rut', 'nombre', 'email', 'telefono', 'es_habitual']  # Datos del cliente
        widgets = {
            'rut': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'es_habitual': forms.CheckboxInput(attrs={'class': 'form-check-input'}),  # Checkbox para cliente habitual
        }

class VentaForm(forms.ModelForm):
    """Formulario para registrar ventas con campos adicionales para cliente"""
    rut_cliente = forms.CharField(
        max_length=12, 
        required=True,  # RUT obligatorio para ventas
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'RUT del cliente'})
    )
    es_cliente_habitual = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='¿Es cliente habitual?'  # Identifica si el cliente es habitual
    )
    
    class Meta:
        model = Venta
        fields = ['producto', 'cantidad_vendida']  # Campos básicos de la venta
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-control'}),
            'cantidad_vendida': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),  # Mínimo 1 unidad
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtra productos: solo muestra aquellos con stock disponible y activos
        self.fields['producto'].queryset = Producto.objects.filter(cantidad__gt=0, activo=True)