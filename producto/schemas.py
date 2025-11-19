from ninja import Schema,ModelSchema
from tienda.models import Tienda
from .models import Producto
from typing import Optional, List

class ProductoSchema(ModelSchema):
    class Meta:
        model=Producto
        fields='__all__'

class ProductoInSchema(Schema):
    nombre: str
    detalles: Optional[str]
    precio: float
    tienda_id: int
    stock: Optional[int] = 0
    # imagen se envía como archivo multipart/form-data en el endpoint, no como URL

class SimpleProductoSchema(Schema):
    id: int
    nombre: str
    