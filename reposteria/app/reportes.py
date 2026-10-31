from datetime import date

from flask import request
from flask_appbuilder import BaseView, expose, has_access
from sqlalchemy import func

from . import appbuilder, db
from .models import ESTADOS, Categoria, Cliente, DetallePedido, Pedido, Producto

IMPORTE = func.sum(DetallePedido.cantidad * DetallePedido.precio_unitario)


def _fecha(nombre):
    raw = request.args.get(nombre, "")
    try:
        return (date.fromisoformat(raw) if raw else None), raw
    except ValueError:
        return None, ""


class ReportesView(BaseView):
    route_base = "/reportes"
    default_view = "ventas"

    @expose("/ventas/")
    @has_access
    def ventas(self):
        desde, desde_raw = _fecha("desde")
        hasta, hasta_raw = _fecha("hasta")
        q = (
            db.session.query(Pedido.fecha, func.count(
                func.distinct(Pedido.id)), IMPORTE)
            .join(DetallePedido, DetallePedido.pedido_id == Pedido.id)
            .filter(Pedido.estado != "Cancelado")
        )
        if desde:
            q = q.filter(Pedido.fecha >= desde)
        if hasta:
            q = q.filter(Pedido.fecha <= hasta)
        filas = q.group_by(Pedido.fecha).order_by(Pedido.fecha).all()
        pie = ["Total", sum(r[1] for r in filas), sum(r[2] for r in filas)]
        return self.render_template(
            "reporte.html",
            titulo="Ventas por rango de fechas",
            filtros=[
                {"name": "desde", "label": "Desde", "valor": desde_raw},
                {"name": "hasta", "label": "Hasta", "valor": hasta_raw},
            ],
            columnas=["Fecha", "Pedidos", "Total vendido"],
            filas=filas,
            pie=pie,
        )

    @expose("/productos/")
    @has_access
    def productos(self):
        desde, desde_raw = _fecha("desde")
        hasta, hasta_raw = _fecha("hasta")
        cat = request.args.get("categoria", "")
        q = (
            db.session.query(
                Producto.nombre, Categoria.nombre, func.sum(
                    DetallePedido.cantidad), IMPORTE
            )
            .join(DetallePedido, DetallePedido.producto_id == Producto.id)
            .join(Categoria, Producto.categoria_id == Categoria.id)
            .join(Pedido, DetallePedido.pedido_id == Pedido.id)
            .filter(Pedido.estado != "Cancelado")
        )
        if cat.isdigit():
            q = q.filter(Categoria.id == int(cat))
        if desde:
            q = q.filter(Pedido.fecha >= desde)
        if hasta:
            q = q.filter(Pedido.fecha <= hasta)
        filas = (
            q.group_by(Producto.id, Producto.nombre, Categoria.nombre)
            .order_by(func.sum(DetallePedido.cantidad).desc())
            .limit(10)
            .all()
        )
        return self.render_template(
            "reporte.html",
            titulo="Productos más vendidos (Top 10)",
            filtros=[
                {"name": "categoria", "label": "Categoría", "valor": cat,
                 "opciones": [(c.id, c.nombre) for c in db.session.query(Categoria)]},
                {"name": "desde", "label": "Desde", "valor": desde_raw},
                {"name": "hasta", "label": "Hasta", "valor": hasta_raw},
            ],
            columnas=["Producto", "Categoría", "Unidades", "Importe"],
            filas=filas,
            pie=None,
        )

    @expose("/saldos/")
    @has_access
    def saldos(self):
        estado = request.args.get("estado", "")
        cliente = request.args.get("cliente", "")
        q = db.session.query(Pedido)
        if estado:
            q = q.filter(Pedido.estado == estado)
        else:
            q = q.filter(Pedido.estado != "Cancelado")
        if cliente.isdigit():
            q = q.filter(Pedido.cliente_id == int(cliente))
        filas = [
            (p.id, p.cliente, p.fecha_entrega,
             p.estado, p.total(), p.pagado(), p.saldo())
            for p in q.order_by(Pedido.fecha_entrega).all()
        ]
        pie = ["", "", "", "Total", sum(f[4] for f in filas),
               sum(f[5] for f in filas), sum(f[6] for f in filas)]
        return self.render_template(
            "reporte.html",
            titulo="Pedidos y saldo por cliente",
            filtros=[
                {"name": "estado", "label": "Estado", "valor": estado,
                 "opciones": [(e, e) for e in ESTADOS]},
                {"name": "cliente", "label": "Cliente", "valor": cliente,
                 "opciones": [(c.id, c.nombre) for c in db.session.query(Cliente)]},
            ],
            columnas=["Pedido", "Cliente", "Entrega",
                      "Estado", "Total", "Pagado", "Saldo"],
            filas=filas,
            pie=pie,
        )


appbuilder.add_view_no_menu(ReportesView)
appbuilder.add_link("Ventas por fechas", href="/reportes/ventas/",
                    category="Reportes", icon="fa-line-chart")
appbuilder.add_link("Productos más vendidos",
                    href="/reportes/productos/", category="Reportes", icon="fa-star")
appbuilder.add_link("Saldos por cliente", href="/reportes/saldos/",
                    category="Reportes", icon="fa-money")
