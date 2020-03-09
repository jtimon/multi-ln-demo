#!/usr/bin/env python3
"""Like pay plugin but if that fails, it tries using gateways instead.
"""
import requests

from hashlib import sha256

from pyln.client import Plugin, LightningRpc

plugin = Plugin()

def check_hash_preimage(payment_hash, payment_preimage):
    hashed_result = sha256(bytes.fromhex(payment_preimage)).hexdigest()
    return hashed_result == payment_hash

def has_error(var_name, var_val):
    plugin.log('GATEPAY: %s (%s)' % (var_name, var_val))
    return not isinstance(var_val, dict) or 'error' in var_val

def _gatepay_with_gateway(lnnode, plugin, bolt11, src_chain_ids, gateway, payment_hash):
    plugin.log('GATEPAY: try to pay using gateway (%s)' % gateway)
    src_invoice = requests.post(gateway + "/request_dest_payment", data={
        'bolt11': bolt11,
        'src_chain_ids': src_chain_ids,
    }).json()
    if has_error('src_invoice', src_invoice):
        return {'error': src_invoice['error']}

    src_payment_result = lnnode.pay(src_invoice['bolt11'])
    if has_error('src_payment_result', src_payment_result):
        return {'error': src_payment_result['error']}

    gateway_confirm_payment_result = requests.post(gateway + "/confirm_src_payment", data={
        'payment_hash': src_payment_result['payment_hash'],
        'payment_preimage': src_payment_result['payment_preimage'],
    }).json()
    if has_error('gateway_confirm_payment_result', gateway_confirm_payment_result):
        return {'error': gateway_confirm_payment_result['error']}

    if check_hash_preimage(payment_hash, gateway_confirm_payment_result['payment_preimage']):
        plugin.log('GATEPAY: Preimage corresponds to payment hash')
        return {
            'payment_hash': payment_hash,
            'payment_preimage': gateway_confirm_payment_result['payment_preimage'],
        }

    msg = 'Preimage doesn\'t corresponds to payment hash. Gateway %s is a scam' % gateway
    plugin.log('GATEPAY: ERROR: %s' % msg)
    return {'error': msg}

@plugin.method("gatepay")
def gatepay(plugin, bolt11, src_chain_ids, gateway, payment_hash):
    """This is like the pay plugin but with more chances to actually pay.

    To have more chances, one needs to configure gateways.
    """
    try:
        lnnode = LightningRpc(plugin.get_option('rpcpath'))
        plugin.log('GATEPAY: try to pay bolt11 normally first (%s)' % bolt11)
        return lnnode.pay(bolt11)

    except Exception as e:
        # TODO try more than one gateway
        # TODO make gateways configurable on clightning
        # gateway = plugin.get_option('gateway')
        if (e.error['code'] == 205 # Invoice is for another network
            or e.error['code'] == -32602 # Invalid bolt11: Unknown chain
            or e.error['code'] == 205 # Could not find a route
        ) and (
            'Invoice is for another network' in e.error['message']
            or 'Invalid bolt11: Unknown chain' in e.error['message']
            or 'Could not find a route' in e.error['message']
        ):
            plugin.log('GATEPAY: error paying normally (%s)' % e.error['message'])
            return _gatepay_with_gateway(lnnode, plugin, bolt11, src_chain_ids, gateway, payment_hash)

    return {'error': 'Error calling gatepay plugin bolt11 %s' % bolt11}

# TODO Introspect this from the clightning node somehow instead of needing a new option
plugin.add_option('rpcpath', '/wd/clightning_datadir_alice/regtest/lightning-rpc', 'The file path to the clightning rpc interface for this node.')
# plugin.add_option('gateway', 'http://bob_gateway:5000', 'Your most trusted gateway starting with b.')
plugin.run()
