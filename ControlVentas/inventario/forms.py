from django import forms
from .models import Producto, Cliente, Venta

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['codigo', 'nombre', 'cantidad', 'precio']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        }

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['rut', 'nombre', 'email', 'telefono', 'es_habitual']
        widgets = {
            'rut': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'es_habitual': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class VentaForm(forms.ModelForm):
    rut_cliente = forms.CharField(
        max_length=12, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'RUT del cliente'})
    )
    es_cliente_habitual = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='¿Es cliente habitual?'
    )
    
    class Meta:
        model = Venta
        fields = ['producto', 'cantidad_vendida']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-control'}),
            'cantidad_vendida': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo mostrar productos con stock disponible
        self.fields['producto'].queryset = Producto.objects.filter(cantidad__gt=0, activo=True)