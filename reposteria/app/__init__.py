import logging
from flask import Flask
from flask_appbuilder import AppBuilder, Model
from flask_sqlalchemy import SQLAlchemy

logging.basicConfig(format="%(asctime)s:%(levelname)s:%(name)s:%(message)s")
logging.getLogger().setLevel(logging.INFO)

app = Flask(__name__)
app.config.from_object("config")
db = SQLAlchemy(app, metadata=Model.metadata)

with app.app_context():
    appbuilder = AppBuilder(app, db.session)
    from . import models, views  # noqa
    db.create_all()
