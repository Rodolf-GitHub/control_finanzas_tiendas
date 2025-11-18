from django.contrib import admin
from .models import Venta


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
	list_display = ('id', 'producto', 'cantidad', 'total_precio', 'fecha_creacion')
	search_fields = ('producto__nombre',)
	list_filter = ('fecha_creacion',)
	readonly_fields = ('fecha_creacion', 'ultima_actualicacion')

