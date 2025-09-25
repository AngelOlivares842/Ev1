from django.db import models
from django.core.validators import MinValueValidator

class Producto(models.Model):
    """Modelo para almacenar información de productos en inventario"""
    codigo = models.CharField(max_length=50, unique=True)  # Código único del producto
    nombre = models.CharField(max_length=100)  # Nombre del producto
    cantidad = models.IntegerField(validators=[MinValueValidator(0)])  # Stock disponible (no negativo)
    precio = models.DecimalField(max_digits=10, decimal_places=2)  # Precio con 2 decimales
    activo = models.BooleanField(default=True)  # Estado del producto (activo/inactivo)
    fecha_creacion = models.DateTimeField(auto_now_add=True)  # Fecha de registro automática
    
    class Meta:
        ordering = ['nombre']  # Ordenar productos por nombre por defecto
    
    def __str__(self):
        return f"{self.nombre} ({self.codigo})"  # Representación legible

class Cliente(models.Model):
    """Modelo para gestionar clientes del sistema"""
    rut = models.CharField(max_length=12, unique=True)  # RUT único del cliente
    nombre = models.CharField(max_length=100)  # Nombre completo
    email = models.EmailField(blank=True, null=True)  # Email opcional
    telefono = models.CharField(max_length=15, blank=True, null=True)  # Teléfono opcional
    es_habitual = models.BooleanField(default=False)  # Identificador de cliente frecuente
    fecha_registro = models.DateTimeField(auto_now_add=True)  # Fecha de registro automática
    
    class Meta:
        ordering = ['nombre']  # Ordenar clientes por nombre
    
    def __str__(self):
        return f"{self.nombre} ({self.rut})"  # Representación legible

class Venta(models.Model):
    """Modelo para registrar transacciones de venta"""
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)  # Producto vendido
    cliente_rut = models.CharField(max_length=12)  # RUT del cliente (siempre requerido)
    cliente_nombre = models.CharField(max_length=100, blank=True, null=True)  # Nombre opcional
    cantidad_vendida = models.IntegerField(validators=[MinValueValidator(1)])  # Mínimo 1 unidad
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)  # Precio al momento de venta
    total = models.DecimalField(max_digits=10, decimal_places=2)  # Total calculado
    fecha_venta = models.DateTimeField(auto_now_add=True)  # Fecha automática de venta
    
    class Meta:
        ordering = ['-fecha_venta']  # Ordenar ventas más recientes primero
    
    def save(self, *args, **kwargs):
        """Sobrescribe save para actualizar stock automáticamente"""
        if not self.pk:  # Solo si es una nueva venta (no actualización)
            self.producto.cantidad -= self.cantidad_vendida  # Reduce stock
            self.producto.save()  # Guarda cambios en producto
        super().save(*args, **kwargs)  # Guarda la venta
    
    def __str__(self):
        return f"Venta {self.id} - {self.producto.nombre}"  # Representación legible