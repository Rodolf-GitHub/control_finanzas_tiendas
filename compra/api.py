from ninja import Router
from .models import Compra
from .schemas import CompraSchema, CompraInSchema
from typing import List, Optional
from ninja.pagination import paginate
from django.shortcuts import get_object_or_404
from producto.models import Producto
from django.utils import timezone
from django.db.models import F
from decimal import Decimal, InvalidOperation
from tienda.models import Tienda
from django.db import transaction

router = Router(tags=["Compra"])

@router.get("/list/{tienda_id}/", response=List[CompraSchema])
@paginate
def list_compras(request, tienda_id: int, dia: Optional[int] = None, mes: Optional[int] = None, ano: Optional[int] = None):
    """
    List all compras for productos in a specific tienda with pagination.
    """
    qs = Compra.objects.filter(producto__tienda_id=tienda_id)
    if dia is not None:
        qs = qs.filter(fecha_creacion__day=dia)
    if mes is not None:
        qs = qs.filter(fecha_creacion__month=mes)
    if ano is not None:
        qs = qs.filter(fecha_creacion__year=ano)
    return qs.order_by('-fecha_creacion')

@router.get("/get/{producto_id}/", response=List[CompraSchema])
@paginate
def list_compras_by_producto(request, producto_id: int, dia: Optional[int] = None, mes: Optional[int] = None, ano: Optional[int] = None):
    """
    List all compras for a specific producto with pagination.
    """
    qs = Compra.objects.filter(producto_id=producto_id)
    if dia is not None:
        qs = qs.filter(fecha_creacion__day=dia)
    if mes is not None:
        qs = qs.filter(fecha_creacion__month=mes)
    if ano is not None:
        qs = qs.filter(fecha_creacion__year=ano)
    return qs.order_by('-fecha_creacion')

@router.post("/create/", response=CompraSchema)
def create_compra(request, compra_in: CompraInSchema):
    """
    Create a new compra.
    """
    producto = get_object_or_404(Producto, id=compra_in.producto_id)
    # calcular total (asegurar Decimal)
    if compra_in.total_precio:
        try:
            total = Decimal(str(compra_in.total_precio))
        except (InvalidOperation, TypeError):
            total = Decimal(producto.precio) * Decimal(compra_in.cantidad)
    else:
        total = Decimal(producto.precio) * Decimal(compra_in.cantidad)
    # normalizar fecha_creacion si viene en el payload, usar hoy si no
    fecha_dt = None
    if getattr(compra_in, 'fecha_creacion', None):
        fecha_dt = compra_in.fecha_creacion
        if timezone.is_naive(fecha_dt):
            fecha_dt = timezone.make_aware(fecha_dt, timezone.get_default_timezone())
        compra_date = fecha_dt.date()
    else:
        compra_date = timezone.localdate()
        fecha_dt = None

    # buscar compra existente del mismo producto en la misma fecha
    compra = Compra.objects.filter(producto=producto, fecha_creacion__date=compra_date).first()
    if compra:
        compra.cantidad = compra.cantidad + compra_in.cantidad
        compra.total_precio = compra.total_precio + total
        compra.save()
        delta = compra_in.cantidad
    else:
        compra = Compra.objects.create(
            producto=producto,
            cantidad=compra_in.cantidad,
            total_precio=total,
            **({'fecha_creacion': fecha_dt} if fecha_dt else {})
        )
        delta = compra_in.cantidad

    # Actualizar el stock del producto (aumenta en la cantidad comprada) usando F() para ser atómico
    Producto.objects.filter(pk=producto.pk).update(stock=F('stock') + delta)
    # refrescar instancia para devolver datos actualizados
    return Compra.objects.get(pk=compra.pk)



@router.post("/bulk/", response=List[CompraSchema])
def create_compras_bulk(request, compras_in: List[CompraInSchema]):
    """
    Crear múltiples compras en una sola petición y actualizar stock por cada una.
    Devuelve la lista de compras creadas (ordenada por creación, más reciente primero).
    """
    created_map = {}  # key: (producto_id, fecha.date()) -> Compra
    stock_deltas = {}
    with transaction.atomic():
        for compra_in in compras_in:
            producto = get_object_or_404(Producto, id=compra_in.producto_id)
            pid = producto.pk
            if compra_in.total_precio:
                try:
                    total = Decimal(str(compra_in.total_precio))
                except (InvalidOperation, TypeError):
                    total = Decimal(producto.precio) * Decimal(compra_in.cantidad)
            else:
                total = Decimal(producto.precio) * Decimal(compra_in.cantidad)

            # Normalizar fecha por item
            fecha_dt = None
            if getattr(compra_in, 'fecha_creacion', None):
                fecha_dt = compra_in.fecha_creacion
                if timezone.is_naive(fecha_dt):
                    fecha_dt = timezone.make_aware(fecha_dt, timezone.get_default_timezone())
                compra_date = fecha_dt.date()
            else:
                compra_date = timezone.localdate()

            key = (pid, compra_date)
            if key in created_map:
                compra = created_map[key]
                compra.cantidad = compra.cantidad + compra_in.cantidad
                compra.total_precio = compra.total_precio + total
                compra.save()
            else:
                # bloquear búsqueda para evitar race por producto+fecha
                existing = Compra.objects.select_for_update().filter(producto=producto, fecha_creacion__date=compra_date).first()
                if existing:
                    existing.cantidad = existing.cantidad + compra_in.cantidad
                    existing.total_precio = existing.total_precio + total
                    existing.save()
                    compra = existing
                else:
                    compra = Compra.objects.create(
                        producto=producto,
                        cantidad=compra_in.cantidad,
                        total_precio=total,
                        **({'fecha_creacion': fecha_dt} if fecha_dt else {})
                    )
                created_map[key] = compra

            stock_deltas[pid] = stock_deltas.get(pid, 0) + compra_in.cantidad

        # aplicar actualizaciones de stock por producto de forma atómica
        for pid, delta in stock_deltas.items():
            Producto.objects.filter(pk=pid).update(stock=F('stock') + delta)

    # devolver las compras afectadas ordenadas por fecha_creacion desc
    created = list(created_map.values())
    return sorted(created, key=lambda c: c.fecha_creacion, reverse=True)

@router.patch("/update/{compra_id}/", response=CompraSchema)
def update_compra(request, compra_id: int, compra_in: CompraInSchema):
    """
    Update an existing compra.
    """
    compra = get_object_or_404(Compra, id=compra_id)
    updates = compra_in.dict(exclude_unset=True)
    # Normalizar fecha_creacion si viene
    if 'fecha_creacion' in updates and updates['fecha_creacion'] is not None:
        fecha_dt = updates['fecha_creacion']
        if timezone.is_naive(fecha_dt):
            fecha_dt = timezone.make_aware(fecha_dt, timezone.get_default_timezone())
        updates['fecha_creacion'] = fecha_dt
    for attr, value in updates.items():
        setattr(compra, attr, value)
    compra.save()
    return compra


@router.delete("/delete/{compra_id}/", response={204: None})
def delete_compra(request, compra_id: int):
    """
    Delete a compra by its ID.
    """
    compra = get_object_or_404(Compra, id=compra_id)
    compra.delete()
    return 204