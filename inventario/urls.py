from rest_framework import routers
from django.urls import path, include
from . import views

router = routers.DefaultRouter()
router.register(r"users", views.UserViewSet)
router.register(r"groups", views.GroupViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("", views.lista_productos, name="lista_productos"),
    path("productos/agregar/", views.agregar_producto, name="agregar_producto"),
    path("productos/editar/<int:pk>/", views.editar_producto, name="editar_producto"),
    path("productos/eliminar/<int:pk>/", views.eliminar_producto, name="eliminar_producto"),  
    path("ventas/", views.lista_ventas, name="lista_ventas"),
    path("ventas/registrar/", views.registrar_venta, name="registrar_venta"),
    path("clientes/registrar/<str:rut>/", views.registrar_cliente_con_rut, name="registrar_cliente_con_rut"),
    
]