from ninja import Schema,ModelSchema
from compra.models import Compra
from typing import Optional

class CompraSchema(ModelSchema):
    class Meta:
        model=Compra
        fields='__all__'

class CompraInSchema(Schema):
    producto_id: int
    cantidad: int
    total_precio: Optional[float] = 0.0

