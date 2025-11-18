from ninja import Router, File, UploadedFile
from tienda.models import Tienda
from tienda.schemas import TiendaSchema, TiendaInSchema
from typing import List, Optional
from ninja.pagination import paginate
from django.shortcuts import get_object_or_404

router = Router(tags=["Tienda"])

@router.get("/", response=List[TiendaSchema])
@paginate
def list_tiendas(request):
    """
    List all tiendas with pagination.
    """
    return Tienda.objects.all()

@router.get("/{tienda_id}/", response=TiendaSchema)
def get_tienda(request, tienda_id: int):
    """
    Retrieve a single tienda by its ID.
    """
    tienda = get_object_or_404(Tienda, id=tienda_id)
    return tienda

@router.post("/", response=TiendaSchema)
def create_tienda(request, tienda_in: TiendaInSchema, imagen: UploadedFile = File(None)):
    """
    Create a new tienda.
    """
    tienda = Tienda.objects.create(**tienda_in.dict())
    if imagen:
        # guardar archivo en el ImageField (usar .name y pasar el UploadedFile)
        tienda.imagen.save(imagen.name, imagen, save=True)
    return tienda

@router.patch("/{tienda_id}/", response=TiendaSchema)
def update_tienda(request, tienda_id: int, tienda_in: TiendaInSchema, imagen: UploadedFile = File(None)):
    """
    Update an existing tienda.
    """
    tienda = get_object_or_404(Tienda, id=tienda_id)
    for attr, value in tienda_in.dict(exclude_unset=True).items():
        setattr(tienda, attr, value)
    if imagen:
        tienda.imagen.save(imagen.name, imagen, save=False)
    tienda.save()
    return tienda

@router.delete("/{tienda_id}/", response={204: None})
def delete_tienda(request, tienda_id: int):
    """
    Delete a tienda by its ID.
    """
    tienda = get_object_or_404(Tienda, id=tienda_id)
    tienda.delete()
    return 204
