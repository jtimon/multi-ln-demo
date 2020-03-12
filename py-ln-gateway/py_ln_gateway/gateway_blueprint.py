
import os

from flask import Blueprint, request

from py_ln_gateway.gateway import Gateway

gateway_blueprint = Blueprint('gateway_blueprint', __name__)

gateway = Gateway(os.environ.get('PYGATEWAY_CONF'))

# TODO Unify to a single POST route with a call_name argument that gets checked on a hardcoded dict and executed dynamically
@gateway_blueprint.route('/get_accepted_chains', methods = ['GET'])
def get_accepted_chains():
    return gateway.get_accepted_chains()

@gateway_blueprint.route('/get_prices', methods = ['GET'])
def get_prices():
    return gateway.get_prices()

@gateway_blueprint.route('/request_dest_payment', methods = ['POST'])
def request_dest_payment():
    req = request.form # a multidict containing POST data
    return gateway.request_dest_payment(req)

@gateway_blueprint.route('/confirm_src_payment', methods = ['POST'])
def confirm_src_payment():
    req = request.form # a multidict containing POST data
    return gateway.confirm_src_payment(req)

@gateway_blueprint.route('/get_payment_proof', methods = ['POST'])
def get_payment_proof():
    return gateway.get_payment_proof(request.form)
