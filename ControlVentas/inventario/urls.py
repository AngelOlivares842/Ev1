from django.urls import path
from . import views

urlpatterns = [
    path("", views.lista_productos, name="lista_productos"),
    path("productos/agregar/", views.agregar_producto, name="agregar_producto"),
    path("productos/editar/<int:pk>/", views.editar_producto, name="editar_producto"),
    path("productos/eliminar/<int:pk>/", views.eliminar_producto, name="eliminar_producto"),  
    path("ventas/", views.lista_ventas, name="lista_ventas"),
    path("ventas/registrar/", views.registrar_venta, name="registrar_venta"),
    path("clientes/registrar/<str:rut>/", views.registrar_cliente_con_rut, name="registrar_cliente_con_rut"),
    
]