from ninja import Router
from .models import Compra
from .schemas import CompraSchema, CompraInSchema
from typing import List
from ninja.pagination import paginate
from django.shortcuts import get_object_or_404
from producto.models import Producto
from tienda.models import Tienda

router = Router(tags=["Compra"])

@router.get("/{tienda_id}/", response=List[CompraSchema])
@paginate
def list_compras(request, tienda_id: int):
    """
    List all compras for productos in a specific tienda with pagination.
    """
    return Compra.objects.filter(producto__tienda_id=tienda_id)

@router.get("/{producto_id}/", response=List[CompraSchema])
@paginate
def list_compras_by_producto(request, producto_id: int):
    """
    List all compras for a specific producto with pagination.
    """
    return Compra.objects.filter(producto_id=producto_id)

@router.post("/", response=CompraSchema)
def create_compra(request, compra_in: CompraInSchema):
    """
    Create a new compra.
    """
    producto = get_object_or_404(Producto, id=compra_in.producto_id)
    compra = Compra.objects.create(
        producto=producto,
        cantidad=compra_in.cantidad,
        total_precio=compra_in.total_precio or producto.precio * compra_in.cantidad
    )
    return compra

@router.patch("/{compra_id}/", response=CompraSchema)
def update_compra(request, compra_id: int, compra_in: CompraInSchema):
    """
    Update an existing compra.
    """
    compra = get_object_or_404(Compra, id=compra_id)
    for attr, value in compra_in.dict(exclude_unset=True).items():
        if attr == "producto_id":
            producto = get_object_or_404(Producto, id=value)
            setattr(compra, "producto", producto)
        else:
            setattr(compra, attr, value)
    compra.save()
    return compra

@router.delete("/{compra_id}/", response={204: None})
def delete_compra(request, compra_id: int):
    """
    Delete a compra by its ID.
    """
    compra = get_object_or_404(Compra, id=compra_id)
    compra.delete()
    return 204