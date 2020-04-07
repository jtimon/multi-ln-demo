
import os

from flask import Blueprint, request

from py_ln_gateway.gateway import Gateway

gatepay_blueprint = Blueprint('gatepay_blueprint', __name__)

gateway = Gateway(os.environ.get('PYGATEWAY_CONF'))

# TODO Unify to a single POST route with a call_name argument that gets checked on a hardcoded dict and executed dynamically
@gatepay_blueprint.route('/get_accepted_chains', methods = ['GET'])
def get_accepted_chains():
    return gateway.get_accepted_chains()

@gatepay_blueprint.route('/get_prices', methods = ['GET'])
def get_prices():
    return gateway.get_prices()

@gatepay_blueprint.route('/request_dest_payment', methods = ['POST'])
def request_dest_payment():
    req = request.form # a multidict containing POST data
    return gateway.request_dest_payment(req)

@gatepay_blueprint.route('/get_payment_proof', methods = ['POST'])
def get_payment_proof():
    return gateway.get_payment_proof(request.form)
