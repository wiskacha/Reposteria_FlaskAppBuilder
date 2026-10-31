from flask import render_template
from flask_appbuilder import ModelView
from flask_appbuilder.models.sqla.interface import SQLAInterface

from . import app, appbuilder, db
from .models import Categoria, Cliente, DetallePedido, Pago, Pedido, Producto


class CategoriaView(ModelView):
    datamodel = SQLAInterface(Categoria)
    list_columns = ["nombre"]


class ProductoView(ModelView):
    datamodel = SQLAInterface(Producto)
    list_columns = ["nombre", "categoria", "precio", "activo"]
    search_columns = ["nombre", "categoria", "activo"]


class ClienteView(ModelView):
    datamodel = SQLAInterface(Cliente)
    list_columns = ["nombre", "telefono", "email"]


class DetallePedidoView(ModelView):
    datamodel = SQLAInterface(DetallePedido)
    list_columns = ["pedido", "producto", "cantidad", "precio_unitario"]


class PagoView(ModelView):
    datamodel = SQLAInterface(Pago)
    list_columns = ["pedido", "monto", "fecha", "metodo"]


class PedidoView(ModelView):
    datamodel = SQLAInterface(Pedido)
    list_columns = ["id", "cliente", "fecha", "fecha_entrega", "estado"]
    search_columns = ["cliente", "fecha", "fecha_entrega", "estado"]
    order_columns = ["id", "fecha", "fecha_entrega", "estado"]
    related_views = [DetallePedidoView, PagoView]
    show_template = "appbuilder/general/model/show_cascade.html"
    edit_template = "appbuilder/general/model/edit_cascade.html"


appbuilder.add_view(CategoriaView, "Categorías",
                    icon="fa-tags", category="Catálogo")
appbuilder.add_view(ProductoView, "Productos",
                    icon="fa-birthday-cake", category="Catálogo")
appbuilder.add_view(ClienteView, "Clientes", icon="fa-users")
appbuilder.add_view(PedidoView, "Pedidos",
                    icon="fa-shopping-basket", category="Ventas")
appbuilder.add_view(DetallePedidoView, "Detalles de pedido",
                    icon="fa-list", category="Ventas")
appbuilder.add_view(PagoView, "Pagos", icon="fa-money", category="Ventas")


@app.errorhandler(404)
def page_not_found(e):
    return (
        render_template(
            "404.html", base_template=appbuilder.base_template, appbuilder=appbuilder
        ),
        404,
    )
