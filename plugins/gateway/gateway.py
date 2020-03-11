#!/usr/bin/env python3
"""Simple plugin to allow testing while closing of HTLC is delayed.
"""

from requests.exceptions import ConnectionError
import requests

from pyln.client import Plugin

plugin = Plugin()

# Example payment:
# {'label': 'from_regtest_to_liquid-regtest_label_5ad2ba3afc73bb3d3db3e80909c75501913abdf79391be1293d0c14fb43dc5b2', 'preimage': '6888a1e103f87233cf8f575de7f6c0db2b0783cd3d2144c20023b0eaa1995eba', 'msat': '1000msat'}

# Example invoice ():
# {'label': 'from_regtest_to_liquid-regtest_label_5ad2ba3afc73bb3d3db3e80909c75501913abdf79391be1293d0c14fb43dc5b2', 'bolt11': 'lnbcrt10n1p0xsfkjpp5tdknedz4t3uhmefjh6dpcgyn55kq6zqr9u8nk0r00rklwx9q7cxsdtzveex7m2lxpnrjvfc8pnrzvmrvgmkyvnrxuckvvnpxven2efnvy6xvcenxguxye34vfjkydpnxccrzvnpve3kzdfexp3rzcf3xy6rvdn9xgerqdjlw3h47wtx8qmk2c348qcxywt9x4nrzvtyvverzvt989nxyd3kv93xyvek8yunjwfexq6rge3cvejnzdpk8qcrzvfkxgenjvenxc6rywpkvvm97cn0d36rzv2lx4skgvnzvyekzenrxuekyc3nvsekgc3nv5urqwfs893nwdf4xqcnjvfnv93xge3h8yenjvtzv5cnywfnvscxxvf5ve3rgvmyvv6kyvjlv3jhxcmjd9c8g6t0dcxqzpucqp2sp52k69yp29ykwxk4al4cg76g32hskuz33llfj7046jna674yle78lq9qy9qsq8j8ll02p7d7qkvc0ns39rlt3hnse8jd5g5d64ehnrdw33wt5up4zwcyfnws28d6ljt3n6hlcfyh4zu9crdnfwkaswfw62379xukj2fqqgullzd', 'payment_hash': '5b6d3cb4555c797de532be9a1c2093a52c0d08032f0f3b3c6f78edf718a0f60d', 'msatoshi': 1000, 'amount_msat': 1000msat, 'status': 'unpaid', 'description': 'from_0f9188f13cb7b2c71f2a335e3a4fc328bf5beb436012afca590b1a11466e2206_to_9f87eb580b9e5f11dc211e9fb66abb3699999044f8fe146801162393364286c6_bolt11_5ad2ba3afc73bb3d3db3e80909c75501913abdf79391be1293d0c14fb43dc5b2_description', 'expires_at': 1583884046}

def has_error(var_name, var_val):
    plugin.log('GATEPAY: %s (%s)' % (var_name, var_val))
    return not isinstance(var_val, dict) or 'error' in var_val

@plugin.hook('invoice_payment')
def on_payment(payment, plugin, **kwargs):
    gateway = plugin.get_option('own_gateway')
    if gateway == '':
        plugin.log('GATEWAY: WARNING: All payments are accepted if own_gateway is not configured')
        return {'result': 'continue'}

    invoice = plugin.rpc.listinvoices(payment['label'])['invoices'][0]
    plugin.log('GATEWAY: receiving a payment:\n%s' % invoice)
    payment_hash = invoice['payment_hash']

    try:
        gateway_confirm_payment_result = requests.post(gateway + "/confirm_src_payment", data={
            'payment_hash': payment_hash,
            'payment_preimage': payment['preimage'],
        }).json()
    except ConnectionError as e:
        plugin.log('GATEWAY: WARNING: Accepting payment because own_gateway seems down (%s)' % payment_hash)
        plugin.log('GATEWAY: WARNING: Exception: %s' % str(e))
        return {'result': 'continue'}

    if has_error('gateway_confirm_payment_result', gateway_confirm_payment_result):
        if gateway_confirm_payment_result['error'] == 'Unkown payment request %s.' % payment_hash:
            plugin.log('GATEWAY: WARNING: Accepting payment with payment_hash unkown to own_gateway (%s)' % payment_hash)
            return {'result': 'continue'}

        plugin.log('GATEWAY: WARNING: Rejecting payment with payment_hash %s' % payment_hash)
        plugin.log('GATEWAY: Rejection error: %s' % gateway_confirm_payment_result['error'])
        return {'result': 'reject'}

    return {'result': 'continue'}

plugin.add_option('own_gateway', '', 'A gateway you control.')
plugin.run()
