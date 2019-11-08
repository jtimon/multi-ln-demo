
from flask import Flask, request
from lightning import LightningRpc

from py_ln_gateway.gateway import Gateway

user_name = 'bob'
gateway = Gateway({
    'chain_1': LightningRpc('/wd/daemon-data/%s_%s/lightning-rpc' % (user_name, 'chain_1')),
    'chain_2': LightningRpc('/wd/daemon-data/%s_%s/lightning-rpc' % (user_name, 'chain_2')),
})
gateway.update_price('chain_1', 'chain_2', 1)

app = Flask(__name__)

@app.route('/request_dest_payment', methods = ['POST'])
def request_dest_payment():
    req = request.form # a multidict containing POST data
    return gateway.request_dest_payment(req)

@app.route('/confirm_src_payment', methods = ['POST'])
def confirm_src_payment():
    req = request.form # a multidict containing POST data
    return gateway.confirm_src_payment(req)
