# check_mongodb.py
import os
import django
from ControlVentas import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ControlVentas.settings')
django.setup()

from inventario.models import Producto

def test_connection():
    try:
        # Intentar contar productos
        count = Producto.objects.count()
        print(f"✅ Conexión exitosa a MongoDB Atlas!")
        print(f"📊 Productos en la base de datos: {count}")
        
        # Crear un producto de prueba
        test_product = Producto.objects.create(
            codigo="TEST001",
            nombre="Producto de Prueba",
            cantidad=100,
            precio=99.99
        )
        print(f"✅ Producto de prueba creado: {test_product}")
        
        # Eliminar producto de prueba
        test_product.delete()
        print("✅ Producto de prueba eliminado")
        
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

if __name__ == "__main__":
    test_connection()