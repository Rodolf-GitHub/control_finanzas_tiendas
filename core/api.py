from ninja import NinjaAPI

from tienda.api import router as tienda_router
from producto.api import router as producto_router
from compra.api import router as compra_router
from venta.api import router as venta_router

api = NinjaAPI()

api.add_router("/tienda/", tienda_router)
api.add_router("/producto/", producto_router)
api.add_router("/compra/", compra_router)
api.add_router("/venta/", venta_router)
