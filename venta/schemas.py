from ninja import Schema,ModelSchema
from tienda.models import Tienda
from typing import Optional
from .models import Venta
from producto.models import Producto

class VentaSchema(ModelSchema):
    class Meta:
        model=Venta
        fields='__all__'

class VentaInSchema(Schema):
    producto_id: int
    cantidad: int
    total_precio: Optional[float] = 0.0