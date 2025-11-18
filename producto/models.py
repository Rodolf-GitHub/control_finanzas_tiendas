from django.db import models
from tienda.models import Tienda
from base_app.models import BaseModel

# Create your models here.
class Producto(BaseModel):
    tienda = models.ForeignKey(Tienda, on_delete=models.CASCADE, related_name='productos')
    nombre = models.CharField(max_length=100)
    detalles = models.TextField()
    stock = models.PositiveIntegerField()
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'productos'
