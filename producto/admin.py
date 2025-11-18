from django.contrib import admin
from django.utils.html import format_html
from django.http import HttpResponseRedirect
from .models import Producto
from tienda.models import Tienda


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
	list_display = ('imagen_tag', 'nombre', 'precio', 'stock', 'fecha_creacion')
	search_fields = ('nombre', 'detalles')
	list_filter = ('tienda', 'fecha_creacion')
	readonly_fields = ('fecha_creacion', 'ultima_actualicacion')

	def imagen_tag(self, obj):
		if obj.imagen and hasattr(obj.imagen, 'url'):
			return format_html('<img src="{}" style="width:60px; height:auto; object-fit:cover;"/>', obj.imagen.url)
		return '-'
	imagen_tag.short_description = 'Imagen'

	def changelist_view(self, request, extra_context=None):
		"""
		Forzar que siempre exista un filtro por `tienda`.
		Si no hay parámetro `tienda__id__exact` en la URL, redirige añadiéndolo
		con la primera tienda disponible (si existe).
		"""
		# Prepare extra context with tiendas for the top dropdown
		tiendas = Tienda.objects.order_by('nombre')
		sel = request.GET.get('tienda__id__exact')

		if 'tienda__id__exact' not in request.GET:
			first_tienda = tiendas.first()
			if first_tienda:
				params = request.GET.copy()
				params['tienda__id__exact'] = str(first_tienda.pk)
				return HttpResponseRedirect(f"{request.path}?{params.urlencode()}")

		extra = extra_context or {}
		extra.update({'tiendas': tiendas, 'selected_tienda': sel})
		return super().changelist_view(request, extra_context=extra)

