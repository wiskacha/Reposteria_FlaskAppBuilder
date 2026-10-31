# Sistema de Gestión para Repostería

Aplicación web desarrollada con **Flask-AppBuilder**, **Python** y **MySQL** para administrar el catálogo, clientes, pedidos y pagos de una repostería, con reportes y control de acceso por roles.

## Integrantes

- Félix Moisés Castellón
- Sergio Viscarra Vargas
- Kevin Escalera Choque

## Tecnologías

- Python 3
- Flask-AppBuilder 5.3.0
- SQLAlchemy / Flask-SQLAlchemy
- MySQL (conector `pymysql`)

## Modelo de datos (6 tablas relacionadas)

```
Categoria 1──N Producto 1──N DetallePedido N──1 Pedido N──1 Cliente
                                                 │
                                                 1
                                                 N
                                               Pago
```

| Tabla | Campos principales |
|---|---|
| `categoria` | id, nombre |
| `producto` | id, nombre, precio, activo, categoria_id |
| `cliente` | id, nombre, telefono, email |
| `pedido` | id, fecha, fecha_entrega, estado, cliente_id |
| `detalle_pedido` | id, cantidad, precio_unitario, pedido_id, producto_id |
| `pago` | id, monto, fecha, metodo, pedido_id |

## Funcionalidades

### CRUD
Listar, crear, consultar, editar y eliminar para todas las tablas.

- **Pedidos**: los detalles y pagos se gestionan desde la vista del pedido (pestañas), con el pedido asignado automáticamente.
- El estado del pedido y el método de pago se eligen desde listas desplegables.
- El total, lo pagado y el saldo se calculan automáticamente.

### Reglas de negocio
- La fecha de entrega no puede ser anterior a la fecha del pedido.
- Al agregar un detalle, el precio unitario se copia del producto (que debe estar activo) y la cantidad debe ser mayor a 0.
- Los pagos deben ser mayores a 0 y no pueden exceder el saldo del pedido.

### Reportes (menú *Reportes*)
| Reporte | Filtros | Ruta |
|---|---|---|
| Ventas por rango de fechas | Desde, Hasta | `/reportes/ventas/` |
| Productos más vendidos (Top 10) | Categoría, Desde, Hasta | `/reportes/productos/` |
| Pedidos y saldo por cliente | Estado, Cliente | `/reportes/saldos/` |

Los pedidos cancelados se excluyen de los reportes salvo que se filtre por ese estado.

### Autenticación y seguridad
- Inicio de sesión obligatorio; todas las vistas están protegidas por permisos.
- **Admin**: acceso total (catálogo, usuarios, seguridad, reportes).
- **Vendedor**: CRUD de clientes, pedidos, detalles y pagos; solo lectura de productos; acceso a reportes y a su perfil. Sin acceso a catálogo ni gestión de usuarios.
- El rol *Vendedor* se crea automáticamente al iniciar la aplicación.

## Estructura del proyecto

```
reposteria/
├── config.py            # Configuración (URI de MySQL, seguridad)
├── run.py               # Punto de entrada
└── app/
    ├── __init__.py      # App Flask, SQLAlchemy y AppBuilder
    ├── models.py        # 6 modelos
    ├── views.py         # Vistas CRUD, menú y rol Vendedor
    ├── reportes.py      # 3 reportes
    └── templates/
        └── reporte.html # Plantilla común de reportes
```

## Cómo levantar el proyecto

### 1. Requisitos
- Python 3.10+
- MySQL en ejecución

### 2. Entorno virtual e instalación

```bash
python -m venv venv
venv\Scripts\activate          # Linux/Mac: source venv/bin/activate
pip install flask-appbuilder pymysql cryptography
```

### 3. Base de datos

```sql
CREATE DATABASE reposteria CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

En `config.py`, configurar la conexión:

```python
SQLALCHEMY_DATABASE_URI = "mysql+pymysql://USUARIO:CLAVE@localhost/reposteria"
```

### 4. Usuario administrador

```bash
cd reposteria
flask --app run fab create-admin
```

### 5. Ejecutar

```bash
flask --app run run
```

Abrir `http://localhost:5000` e iniciar sesión. Las tablas se crean automáticamente en el primer arranque.

### 6. Crear un vendedor
Como Admin: **Seguridad → Listar Usuarios → +**, asignando el rol **Vendedor**. Cerrar sesión e ingresar con ese usuario para probar sus permisos.

## Flujo de uso sugerido

1. Crear categorías y productos (Catálogo).
2. Registrar clientes.
3. Crear un pedido (Ventas → Pedidos) y abrirlo para agregar detalles y pagos.
4. Consultar los reportes en el menú *Reportes*.