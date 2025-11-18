from django.contrib import admin
from .models import Venta


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
	list_display = ('id', 'producto', 'cantidad', 'total_precio', 'created_at')
	search_fields = ('producto__nombre',)
	list_filter = ('created_at',)
	readonly_fields = ('created_at', 'updated_at')

