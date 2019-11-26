from py_ln_gateway.app import app
from py_ln_gateway.db import db

with app.app_context():
    db.create_all()
