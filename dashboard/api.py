from ninja import Router
from .schemas import StoreSummary, TopStore
from tienda.models import Tienda
from django.db.models import Sum, F, Q, Subquery, OuterRef
from producto.models import Producto
from django.utils import timezone
from datetime import timedelta
from typing import Optional

router = Router(tags=["Dashboard"])


def _period_range(period: Optional[str]):
    now = timezone.now()
    if not period or period == "total":
        return None
    if period == "today":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        return start, now
    if period == "week":
        start = (now - timezone.timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
        return start, now
    if period == "month":
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return start, now
    if period == "year":
        start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        return start, now
    # unknown period treated as total
    return None


@router.get("/store-summary/{tienda_id}/", response=StoreSummary)
def store_summary(request, tienda_id: int, period: Optional[str] = None):
    """
    Devuelve resumen para una tienda concreta: total de stock, total gastado en compras,
    total ganado en ventas y balance = ventas - compras.
    `period` puede ser: today, week, month, year, total
    """
    prange = _period_range(period)

    # filtros sobre fecha_creacion de compras/ventas si hay rango
    if prange:
        start, end = prange
        compras_filter = Q(productos__compras__fecha_creacion__gte=start) & Q(productos__compras__fecha_creacion__lte=end)
        ventas_filter = Q(productos__ventas__fecha_creacion__gte=start) & Q(productos__ventas__fecha_creacion__lte=end)
    else:
        compras_filter = Q()
        ventas_filter = Q()

    # Single query over Tienda with annotations
    # Subqueries for top product names (most vendido y mas comprado)
    if prange:
        venta_filter_sub = Q(ventas__fecha_creacion__gte=start) & Q(ventas__fecha_creacion__lte=end)
        compra_filter_sub = Q(compras__fecha_creacion__gte=start) & Q(compras__fecha_creacion__lte=end)
    else:
        venta_filter_sub = Q()
        compra_filter_sub = Q()

    top_vendido_subq = (
        Producto.objects.filter(tienda_id=OuterRef('pk'))
        .annotate(total_vendido=Sum('ventas__cantidad', filter=venta_filter_sub))
        .order_by('-total_vendido')
        .values('nombre')[:1]
    )

    top_comprado_subq = (
        Producto.objects.filter(tienda_id=OuterRef('pk'))
        .annotate(total_comprado=Sum('compras__cantidad', filter=compra_filter_sub))
        .order_by('-total_comprado')
        .values('nombre')[:1]
    )

    qs = Tienda.objects.filter(pk=tienda_id).annotate(
        tienda_nombre=F('nombre'),
        tienda_imagen=F('imagen'),
        total_stock=Sum('productos__stock'),
        compras_total=Sum('productos__compras__total_precio', filter=compras_filter),
        ventas_total=Sum('productos__ventas__total_precio', filter=ventas_filter),
        producto_mas_vendido=Subquery(top_vendido_subq),
        producto_mas_comprado=Subquery(top_comprado_subq),
    )

    tienda = qs.first()
    if not tienda:
        return StoreSummary(
            tienda_id=tienda_id,
            tienda_nombre="",
            total_stock=0,
            compras_total=0,
            ventas_total=0,
            balance=0,
        )

    compras_total = tienda.compras_total or 0
    ventas_total = tienda.ventas_total or 0
    balance = ventas_total - compras_total

    tienda_imagen = getattr(tienda, 'imagen')
    imagen_url = tienda_imagen.url if tienda_imagen else None

    return StoreSummary(
        tienda_id=tienda.pk,
        tienda_nombre=tienda.nombre,
        tienda_imagen=imagen_url,
        total_stock=tienda.total_stock or 0,
        compras_total=compras_total,
        ventas_total=ventas_total,
        balance=balance,
        producto_mas_vendido=getattr(tienda, 'producto_mas_vendido', None),
        producto_mas_comprado=getattr(tienda, 'producto_mas_comprado', None),
    )


@router.get("/top-store/", response=TopStore)
def top_store(request, period: Optional[str] = None):
    """
    Devuelve la tienda con mayor balance en el `period` solicitado.
    """
    prange = _period_range(period)
    if prange:
        start, end = prange
        compras_filter = Q(productos__compras__fecha_creacion__gte=start) & Q(productos__compras__fecha_creacion__lte=end)
        ventas_filter = Q(productos__ventas__fecha_creacion__gte=start) & Q(productos__ventas__fecha_creacion__lte=end)
    else:
        compras_filter = Q()
        ventas_filter = Q()

    qs = Tienda.objects.annotate(
        compras_total=Sum('productos__compras__total_precio', filter=compras_filter),
        ventas_total=Sum('productos__ventas__total_precio', filter=ventas_filter),
    ).annotate(balance=F('ventas_total') - F('compras_total')).order_by('-balance')

    top = qs.first()
    if not top:
        return TopStore(tienda_id=0, tienda_nombre="", balance=0)

    tienda_imagen = getattr(top, 'imagen')
    imagen_url = tienda_imagen.url if tienda_imagen else None
    return TopStore(tienda_id=top.pk, tienda_nombre=top.nombre, tienda_imagen=imagen_url, balance=top.balance or 0)
