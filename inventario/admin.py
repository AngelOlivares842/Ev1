from django.contrib import admin, messages
from django.utils import timezone
from django.urls import path
from django.http import HttpResponse
import csv

from .models import Cliente, Producto, Venta, VentaDetalle


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
			# devolver stock por cada detalle
			for detalle in venta.detalles.all():
				producto = detalle.producto
				producto.cantidad += detalle.cantidad_vendida
				producto.save()
		except Exception:
			continue
		venta.delete()


class VentaDetalleInline(admin.TabularInline):
	model = VentaDetalle
	extra = 0
	readonly_fields = ('subtotal', 'precio_unitario')
	fields = ('producto', 'cantidad_vendida', 'precio_unitario', 'subtotal')


class VentaAdmin(admin.ModelAdmin):
	list_display = ('id', 'cliente_rut', 'cliente_nombre', 'total', 'fecha_venta')
	list_filter = (('fecha_venta', admin.DateFieldListFilter),)
	search_fields = ('cliente_rut', 'cliente_nombre', 'detalles__producto__nombre')
	readonly_fields = ('fecha_venta', 'total')
	actions = [revertir_venta]
	date_hierarchy = 'fecha_venta'
	inlines = [VentaDetalleInline]
	list_per_page = 50

	def get_urls(self):
		urls = super().get_urls()
		custom = [
			path('reporte-por-fechas/', self.admin_site.admin_view(self.report_por_fechas), name='ventas_reporte_por_fechas'),
		]
		return custom + urls

	def report_por_fechas(self, request):
		"""Genera un CSV simple con ventas entre dos fechas proporcionadas como GET: start, end (YYYY-MM-DD)."""
		start = request.GET.get('start')
		end = request.GET.get('end')
		if not start or not end:
			# Mostrar una pequeña ayuda si faltan parámetros
			return HttpResponse("Use ?start=YYYY-MM-DD&end=YYYY-MM-DD para descargar un CSV de ventas en ese rango.")

		qs = Venta.objects.filter(fecha_venta__date__gte=start, fecha_venta__date__lte=end).order_by('fecha_venta')
		# Crear respuesta CSV
		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = f'attachment; filename="ventas_{start}_a_{end}.csv"'
		writer = csv.writer(response)
		writer.writerow(['id', 'fecha_venta', 'cliente_rut', 'cliente_nombre', 'total'])
		for venta in qs:
			writer.writerow([venta.id, venta.fecha_venta.isoformat(), venta.cliente_rut, venta.cliente_nombre or '', venta.total])
		return response


admin.site.register(Cliente, ClienteAdmin)
admin.site.register(Producto, ProductoAdmin)
admin.site.register(Venta, VentaAdmin)
