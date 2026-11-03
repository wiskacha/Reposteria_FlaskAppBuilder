import logging
from flask import Flask, render_template, redirect, url_for
from flask_appbuilder import AppBuilder, Model, IndexView, expose
from flask_sqlalchemy import SQLAlchemy
from flask_login import current_user

logging.basicConfig(
    format="%(asctime)s:%(levelname)s:%(name)s:%(message)s"
)
logging.getLogger().setLevel(logging.INFO)

app = Flask(__name__)
app.config.from_object("config")

db = SQLAlchemy(app, metadata=Model.metadata)


class MyIndexView(IndexView):
    index_template = 'index.html'

    @expose('/')
    def index(self):
        if not current_user.is_authenticated:
            return redirect(url_for('AuthDBView.login'))

        from .models import Cliente, Producto, Pedido
        total_clientes = db.session.query(Cliente).count()
        total_productos = db.session.query(Producto).count()
        total_pedidos = db.session.query(Pedido).count()

        pendientes = db.session.query(Pedido).filter_by(
            estado='Pendiente').count()
        entregados = db.session.query(Pedido).filter_by(
            estado='Entregado').count()
        cancelados = db.session.query(Pedido).filter_by(
            estado='Cancelado').count()

        return self.render_template(
            self.index_template,
            total_clientes=total_clientes,
            total_productos=total_productos,
            total_pedidos=total_pedidos,
            pendientes=pendientes,
            entregados=entregados,
            cancelados=cancelados
        )


with app.app_context():

    appbuilder = AppBuilder(
        app,
        db.session,
        indexview=MyIndexView,
        base_template='my_layout.html'
    )

    from . import models, views
    from . import asistente_ia

    db.create_all()


@app.errorhandler(404)
def page_not_found(e):
    return (
        render_template(
            "404.html", base_template=appbuilder.base_template, appbuilder=appbuilder
        ),
        404,
    )
