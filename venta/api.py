from ninja import Router
from tienda.models import Tienda
from producto.models import Producto
from venta.models import Venta
from .schemas import VentaSchema, VentaInSchema
from typing import List
from ninja.pagination import paginate
from django.shortcuts import get_object_or_404
from django.db import transaction

router = Router(tags=["Venta"])

@router.get("/{tienda_id}/", response=List[VentaSchema])
@paginate
def list_ventas(request, tienda_id: int):
    """
    List all ventas for productos in a specific tienda with pagination.
    """
    return Venta.objects.filter(producto__tienda_id=tienda_id).order_by('-fecha_creacion')


@router.get("/{producto_id}/", response=List[VentaSchema])
@paginate
def list_ventas_by_producto(request, producto_id: int):
    """
    List all ventas for a specific producto with pagination.
    """
    return Venta.objects.filter(producto_id=producto_id).order_by('-fecha_creacion')


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


@router.post("/bulk/", response=List[VentaSchema])
def create_ventas_bulk(request, ventas_in: List[VentaInSchema]):
    """
    Crear múltiples ventas en una sola petición y actualizar stock por cada una.
    Devuelve la lista de ventas creadas (ordenada por creación, más reciente primero).
    """
    created = []
    with transaction.atomic():
        for venta_in in ventas_in:
            producto = get_object_or_404(Producto, id=venta_in.producto_id)
            venta = Venta.objects.create(
                producto=producto,
                cantidad=venta_in.cantidad,
                total_precio=venta_in.total_precio or producto.precio * venta_in.cantidad
            )
            try:
                producto.stock = producto.stock - venta.cantidad
            except Exception:
                producto.stock = -venta.cantidad
            producto.save()
            created.append(venta)
    return sorted(created, key=lambda v: v.fecha_creacion, reverse=True)



@router.delete("/{venta_id}/", response={204: None})
def delete_venta(request, venta_id: int):
    """
    Delete a venta by its ID.
    """
    venta = get_object_or_404(Venta, id=venta_id)
    venta.delete()
    return 204


