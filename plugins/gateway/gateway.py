#!/usr/bin/env python3
"""Simple plugin to allow testing while closing of HTLC is delayed.
"""

from decimal import Decimal
import os

from pyln.client import Plugin

from .models import Price, PendingRequest

plugin = Plugin()

# Example payment:
# {'label': 'from_regtest_to_liquid-regtest_label_5ad2ba3afc73bb3d3db3e80909c75501913abdf79391be1293d0c14fb43dc5b2', 'preimage': '6888a1e103f87233cf8f575de7f6c0db2b0783cd3d2144c20023b0eaa1995eba', 'msat': '1000msat'}

# Example invoice ():
# {'label': 'from_regtest_to_liquid-regtest_label_5ad2ba3afc73bb3d3db3e80909c75501913abdf79391be1293d0c14fb43dc5b2', 'bolt11': 'lnbcrt10n1p0xsfkjpp5tdknedz4t3uhmefjh6dpcgyn55kq6zqr9u8nk0r00rklwx9q7cxsdtzveex7m2lxpnrjvfc8pnrzvmrvgmkyvnrxuckvvnpxven2efnvy6xvcenxguxye34vfjkydpnxccrzvnpve3kzdfexp3rzcf3xy6rvdn9xgerqdjlw3h47wtx8qmk2c348qcxywt9x4nrzvtyvverzvt989nxyd3kv93xyvek8yunjwfexq6rge3cvejnzdpk8qcrzvfkxgenjvenxc6rywpkvvm97cn0d36rzv2lx4skgvnzvyekzenrxuekyc3nvsekgc3nv5urqwfs893nwdf4xqcnjvfnv93xge3h8yenjvtzv5cnywfnvscxxvf5ve3rgvmyvv6kyvjlv3jhxcmjd9c8g6t0dcxqzpucqp2sp52k69yp29ykwxk4al4cg76g32hskuz33llfj7046jna674yle78lq9qy9qsq8j8ll02p7d7qkvc0ns39rlt3hnse8jd5g5d64ehnrdw33wt5up4zwcyfnws28d6ljt3n6hlcfyh4zu9crdnfwkaswfw62379xukj2fqqgullzd', 'payment_hash': '5b6d3cb4555c797de532be9a1c2093a52c0d08032f0f3b3c6f78edf718a0f60d', 'msatoshi': 1000, 'amount_msat': 1000msat, 'status': 'unpaid', 'description': 'from_0f9188f13cb7b2c71f2a335e3a4fc328bf5beb436012afca590b1a11466e2206_to_9f87eb580b9e5f11dc211e9fb66abb3699999044f8fe146801162393364286c6_bolt11_5ad2ba3afc73bb3d3db3e80909c75501913abdf79391be1293d0c14fb43dc5b2_description', 'expires_at': 1583884046}

@plugin.hook('invoice_payment')
def on_payment(payment, plugin, **kwargs):
    if not os.environ.get('GATEWAY_DB'):
        plugin.log('GATEWAY: WARNING: All payments are ignored if env var GATEWAY_DB is not configured')
        return {'result': 'continue'}

    invoice = plugin.rpc.listinvoices(payment['label'])['invoices'][0]
    payment_hash = invoice['payment_hash']
    plugin.log('GATEWAY: receiving a payment:\n%s' % invoice)

    payment_hash = invoice['payment_hash']
    pending_request = PendingRequest.query.get(payment_hash)
    if not pending_request:
        # Ignore payments
        plugin.log('GATEWAY: Ignoring payment hash %s since it\'s not a pending request:\n%s' % payment_hash)
        return {'result': 'continue'}

    if pending_request.other_gw_chain:
        to_pay_chain = pending_request.other_gw_chain
        to_pay_amount = pending_request.other_gw_amount
        to_pay_bolt11 = pending_request.other_gw_bolt11
        to_pay_payment_hash = pending_request.other_gw_payment_hash
    else:
        to_pay_chain = pending_request.dest_chain
        to_pay_amount = pending_request.dest_amount
        to_pay_bolt11 = pending_request.dest_bolt11
        to_pay_payment_hash = pending_request.dest_payment_hash

    # Prices may have been changed from request to confirm call
    # Check the price one more time to mitigate the free option problem. If it fails because of this, a refund is required too.
    price = Price.query.get('%s%s' % (pending_request.src_chain, to_pay_chain))
    if not price or price.price == 0:
        error_msg = "gateway won't receive from chain %s to pay to chain %s" % (
            pending_request.src_chain, pending_request.dest_chain)
        plugin.log('GATEWAY: rejected payment hash %s msg:\n%s' % (payment_hash, error_msg))
        save_failed_request(error_msg, pending_request, payment['preimage'])
        return {'result': 'reject'}

    src_current_offer = to_pay_amount * price.price
    if Decimal(pending_request.src_amount) < src_current_offer:
        error_msg = 'The offered price for payment request %s is no longer accepted. %s' % (payment_hash)
        plugin.log('GATEWAY: rejected payment hash %s msg:\n%s' % (payment_hash, error_msg))
        save_failed_request(error_msg, pending_request, payment_preimage)
        return {'result': 'reject'}

    return {'result': 'continue'}

plugin.run()
