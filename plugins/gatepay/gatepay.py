#!/usr/bin/env python3
"""Like pay plugin but if that fails, it tries using gatepays instead.
"""
import requests

from hashlib import sha256

from pyln.client import Plugin

plugin = Plugin()

chain_ids = {
    'regtest': '0f9188f13cb7b2c71f2a335e3a4fc328bf5beb436012afca590b1a11466e2206',
    'liquid-regtest': '9f87eb580b9e5f11dc211e9fb66abb3699999044f8fe146801162393364286c6',
}

def check_hash_preimage(payment_hash, payment_preimage):
    hashed_result = sha256(bytes.fromhex(payment_preimage)).hexdigest()
    return hashed_result == payment_hash

def has_error(var_name, var_val):
    plugin.log('GATEPAY: %s (%s)' % (var_name, var_val))
    return not isinstance(var_val, dict) or 'error' in var_val

def _gatepay_with_gatepay(plugin, bolt11, gatepay):
    plugin.log('GATEPAY: try to pay using gatepay (%s)' % gatepay)
    src_chain_id = chain_ids[ plugin.rpc.getinfo()['network'] ]
    payment_hash = plugin.rpc.decodepay(bolt11)['payment_hash']

    src_invoice = requests.post(gatepay + "/request_dest_payment", data={
        'bolt11': bolt11,
        'src_chain_ids': [src_chain_id],
    }).json()
    if has_error('src_invoice', src_invoice):
        return {'error': src_invoice['error']}

    src_payment_result = plugin.rpc.pay(src_invoice['bolt11'])
    if has_error('src_payment_result', src_payment_result):
        return {'error': src_payment_result['error']}

    payment_proof = requests.post(gatepay + "/get_payment_proof", data={
        'payment_hash': src_payment_result['payment_hash'],
        'payment_preimage': src_payment_result['payment_preimage'],
    }).json()
    if has_error('payment_proof', payment_proof):
        return {'error': payment_proof['error']}

    if check_hash_preimage(payment_hash, payment_proof['payment_preimage']):
        plugin.log('GATEPAY: Preimage corresponds to payment hash')
        return {
            'payment_hash': payment_hash,
            'payment_preimage': payment_proof['payment_preimage'],
        }

    msg = 'Preimage doesn\'t corresponds to payment hash. Gatepay %s is a scam' % gatepay
    plugin.log('GATEPAY: ERROR: %s' % msg)
    return {'error': msg}

# TODO More elegant way to configure multiple gatepays
GATEPAY_SPLIT_STRING = '::::'

@plugin.method("gatepay")
def gatepay(plugin, bolt11):
    """This is like the pay plugin but with more chances to actually pay.

    To have more chances, one needs to configure gatepays.
    """
    try:
        plugin.log('GATEPAY: try to pay bolt11 normally first (%s)' % bolt11)
        return plugin.rpc.pay(bolt11)

    except Exception as e:
        if (e.error['code'] == 205 # Invoice is for another network
            or e.error['code'] == -32602 # Invalid bolt11: Unknown chain
            or e.error['code'] == 205 # Could not find a route
        ) and (
            'Invoice is for another network' in e.error['message']
            or 'Invalid bolt11: Unknown chain' in e.error['message']
            or 'Could not find a route' in e.error['message']
        ):
            plugin.log('GATEPAY: error paying normally (%s)' % e.error['message'])
            gatepays = plugin.get_option('gatepay').split(GATEPAY_SPLIT_STRING)
            if not gatepays:
                return {'error': 'Gatepay failed to pay normally and there\'s no gatepay configured.'}

            for gatepay in gatepays:
                toreturn = _gatepay_with_gatepay(plugin, bolt11, gatepay)
                if has_error('gatepay', toreturn):
                    return {'error': toreturn['error']}

    return toreturn or {'error': 'Error calling gatepay plugin bolt11 %s' % bolt11}

plugin.add_option('gatepay', '', 'Your most trusted gatepay.')
plugin.run()
