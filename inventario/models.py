from django.db import models, transaction
from django.core.validators import MinValueValidator


class Producto(models.Model):
    """Modelo para almacenar información de productos en inventario"""
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
    """Modelo para gestionar clientes del sistema"""
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
    """Cabecera de venta. El total se calcula sumando los subtotales de sus detalles."""
    cliente_rut = models.CharField(max_length=12)
    cliente_nombre = models.CharField(max_length=100, blank=True, null=True)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    fecha_venta = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_venta']

    def __str__(self):
        return f"Venta {self.id} - {self.cliente_rut} - {self.fecha_venta:%Y-%m-%d %H:%M}"

    def calcular_total(self):
        soma = self.detalles.aggregate(sum=models.Sum('subtotal'))['sum'] or 0
        self.total = soma
        return self.total


class VentaDetalle(models.Model):
    """Detalle de la venta que referencia un `Producto`. Contiene cantidad, precio al momento y subtotal."""
    venta = models.ForeignKey(Venta, related_name='detalles', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad_vendida = models.IntegerField(validators=[MinValueValidator(1)])
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.producto.nombre} x {self.cantidad_vendida}"

    def save(self, *args, **kwargs):
        # Asegura el cálculo correcto del subtotal
        self.subtotal = self.cantidad_vendida * self.precio_unitario
        super().save(*args, **kwargs)