
from flask import Flask

from py_ln_gateway.db import db
from py_ln_gateway.gateway_blueprint import gateway_blueprint

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////wd/py-ln-gateway/py_ln_gateway/gatewaydb.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
app.register_blueprint(gateway_blueprint)
