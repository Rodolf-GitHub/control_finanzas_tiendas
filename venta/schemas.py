from ninja import Schema,ModelSchema
from tienda.models import Tienda
from typing import Optional
from datetime import datetime
from .models import Venta
from producto.models import Producto

class VentaSchema(ModelSchema):
    producto_nombre: Optional[str]
    producto_imagen: Optional[str]
    class Meta:
        model=Venta
        fields='__all__'
    @staticmethod
    def resolve_producto_nombre(venta: Venta) -> Optional[str]:
        return venta.producto.nombre if venta.producto else None
    @staticmethod
    def resolve_producto_imagen(venta: Venta) -> Optional[str]:
        return venta.producto.imagen if venta.producto else None

class VentaInSchema(Schema):
    producto_id: int
    cantidad: int
    total_precio: Optional[float] = 0.0
    fecha_creacion: Optional[datetime] = None  # Opcional: fecha/hora para asignar en creación

class SimpleVentaSchema(Schema):
    id: int
    producto_id: int
    cantidad: int