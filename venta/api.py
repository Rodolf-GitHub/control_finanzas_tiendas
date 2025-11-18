from ninja import Router
from tienda.models import Tienda
from producto.models import Producto
from venta.models import Venta
from .schemas import VentaSchema, VentaInSchema
from typing import List
from ninja.pagination import paginate
from django.shortcuts import get_object_or_404

router = Router(tags=["Venta"])

@router.get("/{tienda_id}/", response=List[VentaSchema])
@paginate
def list_ventas(request, tienda_id: int):
    """
    List all ventas for productos in a specific tienda with pagination.
    """
    return Venta.objects.filter(producto__tienda_id=tienda_id)


@router.get("/{producto_id}/", response=List[VentaSchema])
@paginate
def list_ventas_by_producto(request, producto_id: int):
    """
    List all ventas for a specific producto with pagination.
    """
    return Venta.objects.filter(producto_id=producto_id)

@router.patch("/{venta_id}/", response=VentaSchema)
def update_venta(request, venta_id: int, venta_in: VentaInSchema):
    """
    Update an existing venta.
    """
    venta = get_object_or_404(Venta, id=venta_id)
    for attr, value in venta_in.dict(exclude_unset=True).items():
        setattr(venta, attr, value)
    venta.save()
    return venta

@router.delete("/{venta_id}/", response={204: None})
def delete_venta(request, venta_id: int):
    """
    Delete a venta by its ID.
    """
    venta = get_object_or_404(Venta, id=venta_id)
    venta.delete()
    return 204


