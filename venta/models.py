from django.db import models
from base_app.models import BaseModel
from producto.models import Producto
# Create your models here.
class Venta(BaseModel):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='ventas')
    cantidad = models.PositiveIntegerField()
    total_precio = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'ventas'
