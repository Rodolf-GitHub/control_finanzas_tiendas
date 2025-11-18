from ninja import Schema
from typing import Optional
from decimal import Decimal


class StoreSummary(Schema):
    tienda_id: int
    tienda_nombre: str
    tienda_imagen: Optional[str]
    total_stock: int
    compras_total: Optional[Decimal]
    ventas_total: Optional[Decimal]
    balance: Optional[Decimal]
    producto_mas_vendido: Optional[str]
    producto_mas_comprado: Optional[str]


class TopStore(Schema):
    tienda_id: int
    tienda_nombre: str
    tienda_imagen: Optional[str]
    balance: Optional[Decimal]
