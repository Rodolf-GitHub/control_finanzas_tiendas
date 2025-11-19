from ninja import Router, File, UploadedFile
from tienda.models import Tienda
from tienda.schemas import TiendaSchema, TiendaInSchema
from typing import List, Optional
from ninja.pagination import paginate
from django.shortcuts import get_object_or_404
from django.db.models.functions import TruncDate
from compra.models import Compra
from compra.schemas import CompraSchema, SimpleCompraSchema
from venta.models import Venta
from venta.schemas import VentaSchema, SimpleVentaSchema
from typing import Dict, Any
from datetime import datetime, date
from django.utils import timezone
from producto.models import Producto
from producto.schemas import ProductoSchema, SimpleProductoSchema
from django.db.models import Sum

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


@router.get("/{tienda_id}/recent-activity/", tags=["Tienda"])
def tienda_recent_activity(request, tienda_id: int, limit_ops: int = 10, ref_date: Optional[str] = None) -> Dict[str, Any]:
    """
    Devuelve las últimas `days` fechas (por defecto 4) con actividad de compras y ventas
    en la tienda indicada, y los registros asociados a cada fecha.

    Resultado:
    {
      "compras": [{"date": "2025-11-19", "items": [<Compra>, ...]}, ...],
      "ventas":  [{"date": "2025-11-19", "items": [<Venta>, ...]}, ...]
    }
    """
    tienda = get_object_or_404(Tienda, id=tienda_id)

    # normalizar fecha de referencia (si viene como string ISO) o usar hoy
    if ref_date:
        try:
            # puede venir YYYY-MM-DD o full datetime
            parsed = datetime.fromisoformat(ref_date)
            if isinstance(parsed, datetime):
                if timezone.is_naive(parsed):
                    parsed = timezone.make_aware(parsed, timezone.get_default_timezone())
                ref_dt = parsed.date()
            else:
                ref_dt = parsed
        except Exception:
            try:
                ref_dt = date.fromisoformat(ref_date)
            except Exception:
                ref_dt = timezone.localdate()
    else:
        ref_dt = timezone.localdate()

    # obtener las últimas `limit_ops` operaciones de compras hasta ref_dt
    compras_ops = list(
        Compra.objects.filter(producto__tienda_id=tienda_id, fecha_creacion__date__lte=ref_dt)
        .select_related('producto')
        .order_by('-fecha_creacion')[:limit_ops]
    )

    # extraer fechas distintas preservando orden (más reciente primero), luego invertir para cronológico asc
    compra_dates = []
    for c in compras_ops:
        d = c.fecha_creacion.date()
        if d not in compra_dates:
            compra_dates.append(d)
    compra_dates = list(reversed(compra_dates))

    # obtener todos los productos de la tienda para rellenar con ceros si no hay actividad
    productos = list(Producto.objects.filter(tienda_id=tienda_id))
    productos_map = {p.pk: SimpleProductoSchema(id=p.pk, nombre=p.nombre).dict() for p in productos}

    # ahora devolvemos para cada fecha una lista simple de productos con su cantidad total (incluye 0)
    compras_result = []
    for d in compra_dates:
        # agregamos cantidad total por producto en esa fecha
        aggs = Compra.objects.filter(producto__tienda_id=tienda_id, fecha_creacion__date=d).values('producto_id').annotate(cantidad_sum=Sum('cantidad'))
        agg_map = {a['producto_id']: a['cantidad_sum'] for a in aggs}

        items = []
        for p in productos:
            cantidad = int(agg_map.get(p.pk, 0) or 0)
            items.append({'nombre': productos_map[p.pk]['nombre'], 'cantidad': cantidad})

        compras_result.append({'date': d.isoformat(), 'items': items})

    # ventas: mismas reglas (últimas limit_ops operaciones hasta ref_dt)
    ventas_ops = list(
        Venta.objects.filter(producto__tienda_id=tienda_id, fecha_creacion__date__lte=ref_dt)
        .select_related('producto')
        .order_by('-fecha_creacion')[:limit_ops]
    )

    venta_dates = []
    for v in ventas_ops:
        d = v.fecha_creacion.date()
        if d not in venta_dates:
            venta_dates.append(d)
    venta_dates = list(reversed(venta_dates))

    ventas_result = []
    for d in venta_dates:
        aggs = Venta.objects.filter(producto__tienda_id=tienda_id, fecha_creacion__date=d).values('producto_id').annotate(cantidad_sum=Sum('cantidad'))
        agg_map = {a['producto_id']: a['cantidad_sum'] for a in aggs}

        items = []
        for p in productos:
            cantidad = int(agg_map.get(p.pk, 0) or 0)
            items.append({'nombre': productos_map[p.pk]['nombre'], 'cantidad': cantidad})

        ventas_result.append({'date': d.isoformat(), 'items': items})

    # consolidar en una lista con fecha + operación en el mismo nivel
    activity = []
    for c in compras_result:
        activity.append({
            'date': c['date'],
            'operation': 'compras',
            'items': c['items'],
        })
    for v in ventas_result:
        activity.append({
            'date': v['date'],
            'operation': 'ventas',
            'items': v['items'],
        })

    # añadir lista de inventario actual: id, nombre, stock
    inventory = []
    for p in productos:
        inventory.append({'id': p.pk, 'nombre': p.nombre, 'stock': p.stock})

    return {'activity': activity, 'inventory': inventory}
