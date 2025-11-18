from django.contrib import admin
from .models import Tienda


@admin.register(Tienda)
class TiendaAdmin(admin.ModelAdmin):
	list_display = ('id', 'nombre', 'telefono', 'direccion', 'fecha_creacion')
	search_fields = ('nombre', 'direccion', 'telefono')
	list_filter = ('fecha_creacion',)
	readonly_fields = ('fecha_creacion', 'ultima_actualicacion')

