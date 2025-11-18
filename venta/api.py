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


@router.post("/", response=VentaSchema)
def create_venta(request, venta_in: VentaInSchema):
    """
    Create a new venta and update product stock (decrease).
    """
    producto = get_object_or_404(Producto, id=venta_in.producto_id)
    venta = Venta.objects.create(
        producto=producto,
        cantidad=venta_in.cantidad,
        total_precio=venta_in.total_precio or producto.precio * venta_in.cantidad
    )
    # Actualizar el stock del producto (disminuye en la cantidad vendida)
    try:
        producto.stock = producto.stock - venta.cantidad
    except Exception:
        producto.stock = -venta.cantidad
    producto.save()
    return venta



@router.delete("/{venta_id}/", response={204: None})
def delete_venta(request, venta_id: int):
    """
    Delete a venta by its ID.
    """
    venta = get_object_or_404(Venta, id=venta_id)
    venta.delete()
    return 204


