
from flask import Flask

from py_ln_gateway.db import db_session
from py_ln_gateway.gateway_blueprint import gateway_blueprint

app = Flask(__name__)

app.register_blueprint(gateway_blueprint)

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()
