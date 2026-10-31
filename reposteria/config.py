import os

from flask_appbuilder.security.manager import AUTH_DB

basedir = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = "cambia-esta-clave-por-una-segura"

SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:@localhost/reposteria"
SQLALCHEMY_TRACK_MODIFICATIONS = False

CSRF_ENABLED = True

AUTH_TYPE = AUTH_DB

APP_NAME = "Sistema de Gestión de Repostería"

BABEL_DEFAULT_LOCALE = "es"
BABEL_DEFAULT_FOLDER = "translations"

LANGUAGES = {
    "es": {"flag": "es", "name": "Español"},
    "en": {"flag": "gb", "name": "English"},
}

UPLOAD_FOLDER = os.path.join(basedir, "app", "static", "uploads")
IMG_UPLOAD_FOLDER = UPLOAD_FOLDER
IMG_UPLOAD_URL = "/static/uploads/"