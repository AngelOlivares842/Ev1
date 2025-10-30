from django.contrib import admin, messages
from django.utils import timezone
from .models import Cliente, Producto, Venta


@admin.action(description='Marcar productos seleccionados como activos')
def marcar_activo(modeladmin, request, queryset):
	queryset.update(activo=True)


@admin.action(description='Marcar productos seleccionados como inactivos')
def marcar_inactivo(modeladmin, request, queryset):
	queryset.update(activo=False)


class ProductoAdmin(admin.ModelAdmin):
	list_display = ('codigo', 'nombre', 'cantidad', 'precio', 'activo', 'fecha_creacion')
	list_filter = ('activo', ('fecha_creacion', admin.DateFieldListFilter))
	search_fields = ('codigo', 'nombre')
	actions = [marcar_activo, marcar_inactivo]
	list_per_page = 50

	def delete_model(self, request, obj):
		"""Realizar eliminación lógica desde el admin: marcar `activo=False` en lugar de borrar físicamente."""
		obj.activo = False
		obj.save()
		self.message_user(request, f"Producto '{obj}' marcado como inactivo (eliminación lógica).", level=messages.SUCCESS)

	def delete_queryset(self, request, queryset):
		"""Soporte para borrado por lotes en el admin: establecer `activo=False` para todos los seleccionados."""
		updated = queryset.update(activo=False)
		self.message_user(request, f"Se marcaron {updated} productos como inactivos (eliminación lógica).", level=messages.SUCCESS)

	def get_queryset(self, request):
		"""Por defecto ocultar productos inactivos en la lista del admin.

		- Si el usuario aplica el filtro `activo` en la UI (parámetro `activo__exact`), se devuelve el queryset sin filtrar
		  para que el filtro muestre correctamente activos/inactivos.
		- También se puede forzar mostrar inactivos añadiendo `?show_inactive=1` en la URL del changelist.
		"""
		qs = super().get_queryset(request)
		# Si el parámetro del filtro booleano está en GET, respetar la petición del usuario
		if 'activo__exact' in request.GET or request.GET.get('show_inactive') == '1':
			return qs
		# Por defecto sólo mostrar activos
		return qs.filter(activo=True)


@admin.action(description='Marcar clientes seleccionados como habituales')
def marcar_habitual(modeladmin, request, queryset):
	queryset.update(es_habitual=True)


@admin.action(description='Marcar clientes seleccionados como no habituales')
def marcar_no_habitual(modeladmin, request, queryset):
	queryset.update(es_habitual=False)


class ClienteAdmin(admin.ModelAdmin):
	list_display = ('rut', 'nombre', 'email', 'telefono', 'es_habitual', 'fecha_registro')
	list_filter = ('es_habitual', ('fecha_registro', admin.DateFieldListFilter))
	search_fields = ('rut', 'nombre', 'email')
	actions = [marcar_habitual, marcar_no_habitual]
	list_per_page = 50


@admin.action(description='Revertir venta seleccionada: devolver stock y eliminar venta')
def revertir_venta(modeladmin, request, queryset):
	"""Acción que incrementa el stock del producto y elimina la venta seleccionada.

	Nota: solo aplica a ventas que aún tienen asociado el producto.
	"""
	for venta in queryset:
		try:
			producto = venta.producto
			producto.cantidad += venta.cantidad_vendida
			producto.save()
		except Exception:
			# Si no se puede acceder al producto, saltar esa venta
			continue
		# eliminar la venta
		venta.delete()


class VentaAdmin(admin.ModelAdmin):
	list_display = ('id', 'producto', 'cliente_rut', 'cliente_nombre', 'cantidad_vendida', 'precio_unitario', 'total', 'fecha_venta')
	list_filter = ('producto', ('fecha_venta', admin.DateFieldListFilter))
	search_fields = ('cliente_rut', 'cliente_nombre', 'producto__nombre')
	readonly_fields = ('fecha_venta',)
	actions = [revertir_venta]
	date_hierarchy = 'fecha_venta'
	list_per_page = 50


admin.site.register(Cliente, ClienteAdmin)
admin.site.register(Producto, ProductoAdmin)
admin.site.register(Venta, VentaAdmin)
