from ninja import Schema,ModelSchema
from compra.models import Compra
from typing import Optional
from datetime import datetime

class CompraSchema(ModelSchema):
    producto_nombre: Optional[str]
    producto_imagen: Optional[str]
    class Meta:
        model=Compra
        fields='__all__'
    @staticmethod
    def resolve_producto_nombre(compra: Compra) -> Optional[str]:
        return compra.producto.nombre if compra.producto else None
    @staticmethod
    def resolve_producto_imagen(compra: Compra) -> Optional[str]:
        return compra.producto.imagen if compra.producto else None
    

class CompraInSchema(Schema):
    producto_id: int
    cantidad: int
    total_precio: Optional[float] = 0.0
    fecha_creacion: Optional[datetime] = None  # Opcional: fecha/hora para asignar en creación

class SimpleCompraSchema(Schema):
    id: int
    producto_id: int
    cantidad: int

