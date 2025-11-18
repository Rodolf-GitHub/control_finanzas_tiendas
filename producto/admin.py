from django.contrib import admin
from .models import Producto


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
	list_display = ('id', 'nombre', 'tienda', 'precio', 'stock', 'created_at')
	search_fields = ('nombre', 'detalles')
	list_filter = ('tienda', 'created_at')
	readonly_fields = ('created_at', 'updated_at')

