from ninja import Router, File, UploadedFile
from tienda.models import Tienda
from .models import Producto
from .schemas import ProductoSchema, ProductoInSchema
from typing import List, Optional
from ninja.pagination import paginate
from django.shortcuts import get_object_or_404

router = Router(tags=["Producto"])

@router.get("/list/{tienda_id}/", response=List[ProductoSchema])
@paginate
def list_productos(request, tienda_id: int):
    """
    List all productos for a specific tienda with pagination.
    """
    return Producto.objects.filter(tienda_id=tienda_id)

@router.get("/detalle/{producto_id}/", response=ProductoSchema)
def get_producto(request, producto_id: int):
    """
    Retrieve a single producto by its ID.
    """
    producto = get_object_or_404(Producto, id=producto_id)
    return producto

@router.post("/create/", response=ProductoSchema)
def create_producto(request, producto_in: ProductoInSchema, imagen: UploadedFile = File(None)):
    """
    Create a new producto.
    """
    producto = Producto.objects.create(**producto_in.dict())
    if imagen:
        producto.imagen.save(imagen.name, imagen, save=True)
    return producto

@router.patch("/update/{producto_id}/", response=ProductoSchema)
def update_producto(request, producto_id: int, producto_in: ProductoInSchema, imagen: UploadedFile = File(None)):
    """
    Update an existing producto.
    """
    producto = get_object_or_404(Producto, id=producto_id)
    for attr, value in producto_in.dict(exclude_unset=True).items():
        setattr(producto, attr, value)
    if imagen:
        producto.imagen.save(imagen.name, imagen, save=False)
    producto.save()
    return producto

@router.delete("/delete/{producto_id}/", response={204: None})
def delete_producto(request, producto_id: int):
    """
    Delete a producto by its ID.
    """
    producto = get_object_or_404(Producto, id=producto_id)
    producto.delete()
    return 204
