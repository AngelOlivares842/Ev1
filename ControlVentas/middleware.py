from django.db import utils as db_utils
from django.shortcuts import render


class DatabaseExceptionMiddleware:
    """Middleware que intercepta fallos de conexión a la base de datos
    y devuelve una página de servicio no disponible (503) en lugar de 500.
    Esto evita que cada operación CRUD muestre un traceback si la DB no está
    disponible temporalmente (p. ej. problemas de red en el proveedor).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
        except db_utils.OperationalError:
            # Retorna una plantilla simple de mantenimiento/DB no disponible
            return render(request, 'inventario/db_unavailable.html', status=503)
        return response
