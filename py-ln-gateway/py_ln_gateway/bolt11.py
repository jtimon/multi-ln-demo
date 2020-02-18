
import re

from py_ln_gateway.bech32 import bech32_decode
from py_ln_gateway.models import MAX_BOLT11

def bolt11_decode(bolt11):
    if len(bolt11) > MAX_BOLT11:
        return {'error': "Bolt11 invoices above %s in length are rejected" % MAX_BOLT11}

    hrp, data = bech32_decode(bolt11)
    if not hrp:
        return {'error': "Bad bech32 checksum for bolt11"}

    # BOLT #11:
    #
    # A reader MUST fail if it does not understand the `prefix`
    if not hrp.startswith('ln'):
        return {'error': "Bad bolt11, hrp does not start with ln"}

    m = re.search("[^\d]+", hrp[2:])
    if not m:
        return {'error': "No chain/currency bip173 name in bolt11"}

    decoded_bolt11 = {}
    decoded_bolt11['currency'] = m.group(0)

    return decoded_bolt11
