import os
from dotenv import load_dotenv
from flask_appbuilder.security.manager import AUTH_DB


load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = os.getenv(
    "SECRET_KEY", "cambia-esta-clave-por-una-segura-en-.env")

SQLALCHEMY_DATABASE_URI = os.getenv(
    "SQLALCHEMY_DATABASE_URI",
    "mysql+pymysql://root:passwod@localhost:3306/reposteria"
)
SQLALCHEMY_TRACK_MODIFICATIONS = False

CSRF_ENABLED = True
AUTH_TYPE = AUTH_DB

APP_NAME = "Sistema de Gestión de Repostería"
APP_ICON = "/static/favicon.ico"

BABEL_DEFAULT_LOCALE = "es"
BABEL_DEFAULT_FOLDER = "translations"

LANGUAGES = {
    "es": {"flag": "es", "name": "Español"},
    "en": {"flag": "gb", "name": "English"},
}

UPLOAD_FOLDER = os.path.join(basedir, "app", "static", "uploads")
IMG_UPLOAD_FOLDER = UPLOAD_FOLDER
IMG_UPLOAD_URL = "/static/uploads/"
