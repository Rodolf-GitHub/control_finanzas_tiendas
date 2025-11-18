from ninja import Router
from tienda.models import Tienda
from producto.models import Producto
from venta.models import Venta
from .schemas import VentaSchema, VentaInSchema
from typing import List, Optional
from ninja.pagination import paginate
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from django.db.models import F
from decimal import Decimal, InvalidOperation

router = Router(tags=["Venta"])

@router.get("/list/{tienda_id}/", response=List[VentaSchema])
@paginate
def list_ventas(request, tienda_id: int, dia: Optional[int] = None, mes: Optional[int] = None, ano: Optional[int] = None):
    """
    List all ventas for productos in a specific tienda with pagination.
    """
    qs = Venta.objects.filter(producto__tienda_id=tienda_id)
    if dia is not None:
        qs = qs.filter(fecha_creacion__day=dia)
    if mes is not None:
        qs = qs.filter(fecha_creacion__month=mes)
    if ano is not None:
        qs = qs.filter(fecha_creacion__year=ano)
    return qs.order_by('-fecha_creacion')


@router.get("/get/{producto_id}/", response=List[VentaSchema])
@paginate
def list_ventas_by_producto(request, producto_id: int, dia: Optional[int] = None, mes: Optional[int] = None, ano: Optional[int] = None):
    """
    List all ventas for a specific producto with pagination.
    """
    qs = Venta.objects.filter(producto_id=producto_id)
    if dia is not None:
        qs = qs.filter(fecha_creacion__day=dia)
    if mes is not None:
        qs = qs.filter(fecha_creacion__month=mes)
    if ano is not None:
        qs = qs.filter(fecha_creacion__year=ano)
    return qs.order_by('-fecha_creacion')


@router.post("/create/", response=VentaSchema)
def create_venta(request, venta_in: VentaInSchema):
    """
    Create a new venta and update product stock (decrease).
    """
    producto = get_object_or_404(Producto, id=venta_in.producto_id)
    if venta_in.total_precio:
        try:
            total = Decimal(str(venta_in.total_precio))
        except (InvalidOperation, TypeError):
            total = Decimal(producto.precio) * Decimal(venta_in.cantidad)
    else:
        total = Decimal(producto.precio) * Decimal(venta_in.cantidad)
    hoy = timezone.localdate()
    venta = Venta.objects.filter(producto=producto, fecha_creacion__date=hoy).first()
    if venta:
        venta.cantidad = venta.cantidad + venta_in.cantidad
        venta.total_precio = venta.total_precio + total
        venta.save()
        delta = venta_in.cantidad
    else:
        venta = Venta.objects.create(
            producto=producto,
            cantidad=venta_in.cantidad,
            total_precio=total
        )
        delta = venta_in.cantidad

    # Disminuir stock usando F() para ser atómico
    Producto.objects.filter(pk=producto.pk).update(stock=F('stock') - delta)
    return Venta.objects.get(pk=venta.pk)


@router.post("/bulk/", response=List[VentaSchema])
def create_ventas_bulk(request, ventas_in: List[VentaInSchema]):
    """
    Crear múltiples ventas en una sola petición y actualizar stock por cada una.
    Devuelve la lista de ventas creadas (ordenada por creación, más reciente primero).
    """
    created_map = {}
    stock_deltas = {}
    hoy = timezone.localdate()
    with transaction.atomic():
        for venta_in in ventas_in:
            producto = get_object_or_404(Producto, id=venta_in.producto_id)
            pid = producto.pk
            if venta_in.total_precio:
                try:
                    total = Decimal(str(venta_in.total_precio))
                except (InvalidOperation, TypeError):
                    total = Decimal(producto.precio) * Decimal(venta_in.cantidad)
            else:
                total = Decimal(producto.precio) * Decimal(venta_in.cantidad)

            if pid in created_map:
                venta = created_map[pid]
                venta.cantidad = venta.cantidad + venta_in.cantidad
                venta.total_precio = venta.total_precio + total
                venta.save()
            else:
                existing = Venta.objects.select_for_update().filter(producto=producto, fecha_creacion__date=hoy).first()
                if existing:
                    existing.cantidad = existing.cantidad + venta_in.cantidad
                    existing.total_precio = existing.total_precio + total
                    existing.save()
                    venta = existing
                else:
                    venta = Venta.objects.create(
                        producto=producto,
                        cantidad=venta_in.cantidad,
                        total_precio=total
                    )
                created_map[pid] = venta

            stock_deltas[pid] = stock_deltas.get(pid, 0) + venta_in.cantidad

        for pid, delta in stock_deltas.items():
            Producto.objects.filter(pk=pid).update(stock=F('stock') - delta)

    created = list(created_map.values())
    return sorted(created, key=lambda v: v.fecha_creacion, reverse=True)

@router.patch("/update/{venta_id}/", response=VentaSchema)
def update_venta(request, venta_id: int, venta_in: VentaInSchema):
    """
    Update an existing venta.
    """
    venta = get_object_or_404(Venta, id=venta_id)
    for attr, value in venta_in.dict(exclude_unset=True).items():
        setattr(venta, attr, value)
    venta.save()
    return venta

@router.delete("/delete/{venta_id}/", response={204: None})
def delete_venta(request, venta_id: int):
    """
    Delete a venta by its ID.
    """
    venta = get_object_or_404(Venta, id=venta_id)
    venta.delete()
    return 204


