from django.db import models

# Create your models here.
class BaseModel(models.Model):
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    ultima_actualicacion = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
