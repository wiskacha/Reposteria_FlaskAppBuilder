from flask import render_template
from flask_appbuilder import ModelView
from flask_appbuilder.models.sqla.interface import SQLAInterface

from datetime import date
from . import app, appbuilder, db
from wtforms import SelectField
from .models import ESTADOS, METODOS, Categoria, Cliente, DetallePedido, Pago, Pedido, Producto


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
    add_columns = ["pedido", "producto", "cantidad"]
    edit_columns = ["producto", "cantidad", "precio_unitario"]

    def pre_add(self, item):
        if item.cantidad < 1:
            raise ValueError("La cantidad debe ser mayor a 0")
        if not item.producto.activo:
            raise ValueError("El producto no está activo")
        item.precio_unitario = item.producto.precio

    def pre_update(self, item):
        if item.cantidad < 1 or item.precio_unitario < 0:
            raise ValueError("Cantidad o precio inválidos")


class PagoView(ModelView):
    datamodel = SQLAInterface(Pago)
    list_columns = ["pedido", "monto", "fecha", "metodo"]
    add_columns = ["pedido", "monto", "fecha", "metodo"]
    add_form_extra_fields = {"metodo": SelectField("Método", choices=METODOS)}
    edit_form_extra_fields = {"metodo": SelectField("Método", choices=METODOS)}

    edit_columns = ["monto", "fecha", "metodo"]

    def _validar(self, item):
        pedido = item.pedido
        if item.monto <= 0:
            raise ValueError("El monto debe ser mayor a 0")
        otros = sum(p.monto for p in pedido.pagos if p is not item)
        saldo = pedido.total() - otros
        if item.monto > saldo:
            raise ValueError(f"El monto excede el saldo ({saldo})")

    pre_add = _validar
    pre_update = _validar


class PedidoView(ModelView):
    datamodel = SQLAInterface(Pedido)
    list_columns = ["id", "cliente", "fecha", "fecha_entrega", "estado"]
    search_columns = ["cliente", "fecha", "fecha_entrega", "estado"]
    order_columns = ["id", "fecha", "fecha_entrega", "estado"]
    related_views = [DetallePedidoView, PagoView]
    show_template = "appbuilder/general/model/show_cascade.html"
    edit_template = "appbuilder/general/model/edit_cascade.html"
    add_columns = ["cliente", "fecha_entrega", "estado"]
    edit_columns = ["cliente", "fecha_entrega", "estado"]
    add_form_extra_fields = {"estado": SelectField("Estado", choices=ESTADOS)}
    edit_form_extra_fields = {"estado": SelectField("Estado", choices=ESTADOS)}
    show_columns = ["cliente", "fecha", "fecha_entrega",
                    "estado", "total", "pagado", "saldo"]
    label_columns = {
        "total": "Total", "pagado": "Pagado", "saldo": "Saldo",
        "fecha_entrega": "Fecha de entrega", "cliente": "Cliente",
    }

    def pre_add(self, item):
        if item.fecha_entrega < (item.fecha or date.today()):
            raise ValueError(
                "La fecha de entrega no puede ser anterior a la del pedido")

    pre_update = pre_add


appbuilder.add_view(CategoriaView, "Categorías",
                    icon="fa-tags", category="Catálogo")
appbuilder.add_view(ProductoView, "Productos",
                    icon="fa-birthday-cake", category="Catálogo")
appbuilder.add_view(ClienteView, "Clientes", icon="fa-users")
appbuilder.add_view(PedidoView, "Pedidos",
                    icon="fa-shopping-basket", category="Ventas")
appbuilder.add_view_no_menu(DetallePedidoView)
appbuilder.add_view_no_menu(PagoView)


@app.errorhandler(404)
def page_not_found(e):
    return (
        render_template(
            "404.html", base_template=appbuilder.base_template, appbuilder=appbuilder
        ),
        404,
    )


CRUD = ["can_list", "can_show", "can_add", "can_edit", "can_delete"]
PERMISOS_VENDEDOR = {
    # vistas
    "ClienteView": CRUD,
    "PedidoView": CRUD,
    "DetallePedidoView": CRUD,
    "PagoView": CRUD,
    "ProductoView": ["can_list", "can_show"],
    # menús (por etiqueta)
    "Clientes": ["menu_access"],
    "Ventas": ["menu_access"],
    "Pedidos": ["menu_access"],
    "Detalles de pedido": ["menu_access"],
    "Pagos": ["menu_access"],
    # perfil
    "UserDBModelView": ["can_userinfo", "userinfoedit", "resetmypassword"],
    "UserInfoEditView": ["can_this_form_get", "can_this_form_post"],
    "ResetMyPasswordView": ["can_this_form_get", "can_this_form_post"],
}


def crear_rol_vendedor():
    sm = appbuilder.sm
    rol = sm.find_role("Vendedor") or sm.add_role("Vendedor")
    for vista, perms in PERMISOS_VENDEDOR.items():
        for perm in perms:
            pv = sm.find_permission_view_menu(perm, vista)
            if not pv:
                print(f"[permiso no encontrado] {perm} / {vista}")
            elif pv not in rol.permissions:
                sm.add_permission_role(rol, pv)


crear_rol_vendedor()
