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
    descripcion: Optional[str]
    precio: float
    tienda_id: int
    stock: Optional[int] = 0
    imagen: Optional[str] = None