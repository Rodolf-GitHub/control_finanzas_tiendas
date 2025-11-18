from django.db import models
from base_app.models import BaseModel

# Create your models here.
class Tienda(BaseModel):
    imagen = models.ImageField(upload_to='tienda/imagenes/', null=True, blank=True)
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255,null=True, blank=True)
    telefono = models.CharField(max_length=20,null=True, blank=True)
    descripcion = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'tiendas'
    
    def __str__(self):
        return self.nombre
