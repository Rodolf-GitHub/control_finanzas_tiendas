from ninja import Schema,ModelSchema
from tienda.models import Tienda
from typing import Optional

class TiendaSchema(ModelSchema):
    class Meta:
        model = Tienda
        fields = '__all__'

class TiendaInSchema(Schema):
    nombre: str
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    descripcion: Optional[str] = None
    imagen: Optional[str] = None
    