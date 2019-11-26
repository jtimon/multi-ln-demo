
from flask import Flask, request

from py_ln_gateway import db
from py_ln_gateway.gateway import Gateway
from py_ln_gateway.models import Price

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////wd/py-ln-gateway/py_ln_gateway/gatewaydb.db"
db.init_app(app)

# TODO is this the best way to avoid the with above within gateway.py ?
app.app_context().push()

# TODO FIX DB don't run every time
db.create_all()

# TODO Run from a cron job like if it was pulling data from an exchange or something.
# Alternatively expose an authenticated API to update prices so that it can
# be used to update prices continuously by calling or subscribing
# to an external API. And call that instead of running this.
db.session.add(Price(
    src_chain = '58ebd25d25b128530d4d462c65a7e679b7e053e6f25ffb8ac63bc68832fda201',
    dest_chain = 'e07d79a4f8f1525814e421eb71aa9527fe8a25091fe1b9c5c312939c887aadc7',
    price = 1))
db.session.commit()

gateway = Gateway('/wd/py-ln-gateway/py_ln_gateway/nodes_config.json')

@app.route('/get_accepted_chains', methods = ['GET'])
def get_accepted_chains():
    return gateway.get_accepted_chains()

@app.route('/get_prices', methods = ['GET'])
def get_prices():
    return gateway.get_prices()

@app.route('/request_dest_payment', methods = ['POST'])
def request_dest_payment():
    req = request.form # a multidict containing POST data
    return gateway.request_dest_payment(req)

@app.route('/confirm_src_payment', methods = ['POST'])
def confirm_src_payment():
    req = request.form # a multidict containing POST data
    return gateway.confirm_src_payment(req)
