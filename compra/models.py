from base_app.models import BaseModel
from producto.models import Producto
from django.db import models
class Compra(BaseModel):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='compras')
    cantidad = models.PositiveIntegerField()
    total_precio = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'compras'