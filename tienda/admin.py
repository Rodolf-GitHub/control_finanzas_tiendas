from django.contrib import admin
from .models import Tienda


@admin.register(Tienda)
class TiendaAdmin(admin.ModelAdmin):
	list_display = ('id', 'nombre', 'telefono', 'direccion', 'created_at')
	search_fields = ('nombre', 'direccion', 'telefono')
	list_filter = ('created_at',)
	readonly_fields = ('created_at', 'updated_at')

