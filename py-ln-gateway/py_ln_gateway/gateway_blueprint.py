
import os

from flask import Blueprint, request

from py_ln_gateway.gateway import Gateway

gateway_blueprint = Blueprint('gateway_blueprint', __name__)

gateway = Gateway(os.environ.get('PYGATEWAY_CONF'))

@gateway_blueprint.route('/confirm_src_payment', methods = ['POST'])
def confirm_src_payment():
    req = request.form # a multidict containing POST data
    return gateway.confirm_src_payment(req)
