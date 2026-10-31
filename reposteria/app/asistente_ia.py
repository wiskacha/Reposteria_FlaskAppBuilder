import os

from flask import request
from flask_wtf.csrf import generate_csrf
from flask_appbuilder import BaseView, expose, has_access
from groq import Groq

from . import appbuilder, db
from .models import Producto


class AsistenteIAView(BaseView):
    route_base = "/asistente"
    default_view = "chat"

    @expose("/", methods=["GET", "POST"])
    @has_access
    def chat(self):
        respuesta = None
        pregunta = ""

        if request.method == "POST":
            pregunta = request.form.get("pregunta", "").strip()

            if not pregunta:
                respuesta = "Escribe una pregunta."

            elif len(pregunta) > 1000:
                respuesta = "La pregunta no puede superar los 1000 caracteres."

            else:
                try:
                    api_key = os.getenv("GROQ_API_KEY")

                    if not api_key:
                        raise ValueError("No se configuró la API Key de Groq.")

                    productos = (
                        db.session.query(Producto)
                        .filter_by(activo=True)
                        .all()
                    )

                    catalogo = "\n".join(
                        f"- {p.nombre}: Bs {p.precio} "
                        f"(Categoría: {p.categoria.nombre})"
                        for p in productos
                    )

                    if not catalogo:
                        catalogo = "No hay productos registrados actualmente."

                    client = Groq(api_key=api_key)

                    resultado = client.chat.completions.create(
                        model="openai/gpt-oss-20b",
                        messages=[
                            {
                                "role": "system",
                                "content": (
                                    "Eres el asistente virtual de una repostería. "
                                    "Responde siempre en español. "
                                    "Ayuda a los clientes a elegir productos. "
                                    "Utiliza exclusivamente los productos y precios "
                                    "del catálogo proporcionado. "
                                    "No inventes productos, precios ni disponibilidad. "
                                    "Si el catálogo está vacío, informa al usuario.\n\n"
                                    "CATÁLOGO:\n" + catalogo
                                )
                            },
                            {
                                "role": "user",
                                "content": pregunta
                            }
                        ],
                        temperature=0.5
                    )

                    respuesta = resultado.choices[0].message.content

                except Exception as error:
                    print("ERROR ASISTENTE IA:", error)
                    respuesta = (
                        "No se pudo obtener una respuesta. "
                        "Revisa la conexión con Groq y la configuración de la API."
                    )

        return self.render_template(
            "asistente.html",
            respuesta=respuesta,
            pregunta=pregunta,
            csrf_token=generate_csrf()
        )


appbuilder.add_view(
    AsistenteIAView,
    "Asistente IA",
    icon="fa-comments",
    category="Herramientas"
)