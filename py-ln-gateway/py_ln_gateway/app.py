
from flask import Flask, request
from lightning import LightningRpc

from py_ln_gateway.gateway import Gateway

# TODO Make sibling_nodes customiable via file
user_name = 'bob'
gateway = Gateway({
    # chain_1 bip173: bca
    '58ebd25d25b128530d4d462c65a7e679b7e053e6f25ffb8ac63bc68832fda201': LightningRpc('/wd/daemon-data/%s_%s/lightning-rpc' % (user_name, 'chain_1')),
    # chain_2 bip173: bcb
    'e07d79a4f8f1525814e421eb71aa9527fe8a25091fe1b9c5c312939c887aadc7': LightningRpc('/wd/daemon-data/%s_%s/lightning-rpc' % (user_name, 'chain_2')),
})
gateway.update_price('58ebd25d25b128530d4d462c65a7e679b7e053e6f25ffb8ac63bc68832fda201', 'e07d79a4f8f1525814e421eb71aa9527fe8a25091fe1b9c5c312939c887aadc7', 1)

app = Flask(__name__)

@app.route('/request_dest_payment', methods = ['POST'])
def request_dest_payment():
    req = request.form # a multidict containing POST data
    return gateway.request_dest_payment(req)

@app.route('/confirm_src_payment', methods = ['POST'])
def confirm_src_payment():
    req = request.form # a multidict containing POST data
    return gateway.confirm_src_payment(req)
