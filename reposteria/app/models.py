from datetime import date

from flask_appbuilder import Model
from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

ESTADOS = ["Pendiente", "Entregado", "Cancelado"]
METODOS = ["Efectivo", "Tarjeta", "Transferencia"]


class Categoria(Model):
    __tablename__ = "categoria"
    id = Column(Integer, primary_key=True)
    nombre = Column(String(80), unique=True, nullable=False)

    def __repr__(self):
        return self.nombre


class Producto(Model):
    __tablename__ = "producto"
    id = Column(Integer, primary_key=True)
    nombre = Column(String(120), nullable=False)
    precio = Column(Numeric(10, 2), nullable=False)
    activo = Column(Boolean, default=True)
    categoria_id = Column(Integer, ForeignKey("categoria.id"), nullable=False)
    categoria = relationship("Categoria")

    def __repr__(self):
        return self.nombre


class Cliente(Model):
    __tablename__ = "cliente"
    id = Column(Integer, primary_key=True)
    nombre = Column(String(120), nullable=False)
    telefono = Column(String(20))
    email = Column(String(120))

    def __repr__(self):
        return self.nombre


class Pedido(Model):
    __tablename__ = "pedido"
    id = Column(Integer, primary_key=True)
    fecha = Column(Date, default=date.today, nullable=False)
    fecha_entrega = Column(Date, nullable=False)
    estado = Column(String(20), default="Pendiente", nullable=False)
    cliente_id = Column(Integer, ForeignKey("cliente.id"), nullable=False)
    cliente = relationship("Cliente")
    detalles = relationship("DetallePedido", cascade="all, delete-orphan")
    pagos = relationship("Pago", cascade="all, delete-orphan")

    def total(self):
        return sum(d.cantidad * d.precio_unitario for d in self.detalles)

    def pagado(self):
        return sum(p.monto for p in self.pagos)

    def saldo(self):
        return self.total() - self.pagado()

    def __repr__(self):
        return f"Pedido #{self.id}"


class DetallePedido(Model):
    __tablename__ = "detalle_pedido"
    id = Column(Integer, primary_key=True)
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Numeric(10, 2), nullable=False)
    pedido_id = Column(Integer, ForeignKey("pedido.id"), nullable=False)
    producto_id = Column(Integer, ForeignKey("producto.id"), nullable=False)
    pedido = relationship("Pedido", back_populates="detalles")
    producto = relationship("Producto")

    def subtotal(self):
        return self.cantidad * self.precio_unitario

    def __repr__(self):
        return f"{self.producto} x{self.cantidad}"


class Pago(Model):
    __tablename__ = "pago"
    id = Column(Integer, primary_key=True)
    monto = Column(Numeric(10, 2), nullable=False)
    fecha = Column(Date, default=date.today, nullable=False)
    metodo = Column(String(20), nullable=False)
    pedido_id = Column(Integer, ForeignKey("pedido.id"), nullable=False)
    pedido = relationship("Pedido", back_populates="pagos")

    def __repr__(self):
        return f"{self.metodo} ${self.monto}"
