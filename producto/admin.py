from django.contrib import admin
from .models import Producto


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
	list_display = ('id', 'nombre', 'tienda', 'precio', 'stock', 'fecha_creacion')
	search_fields = ('nombre', 'detalles')
	list_filter = ('tienda', 'fecha_creacion')
	readonly_fields = ('fecha_creacion', 'ultima_actualicacion')

