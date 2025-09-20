from django.db import models
from django.core.validators import MinValueValidator

class Producto(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=100)
    cantidad = models.IntegerField(validators=[MinValueValidator(0)])
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.nombre} ({self.codigo})"

class Cliente(models.Model):
    rut = models.CharField(max_length=12, unique=True)
    nombre = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    es_habitual = models.BooleanField(default=False)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.nombre} ({self.rut})"

class Venta(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cliente_rut = models.CharField(max_length=12)
    cliente_nombre = models.CharField(max_length=100, blank=True, null=True)
    cantidad_vendida = models.IntegerField(validators=[MinValueValidator(1)])
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_venta = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-fecha_venta']
    
    def save(self, *args, **kwargs):
        # Actualizar stock del producto
        if not self.pk:  # Solo si es nueva venta
            self.producto.cantidad -= self.cantidad_vendida
            self.producto.save()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Venta {self.id} - {self.producto.nombre}"