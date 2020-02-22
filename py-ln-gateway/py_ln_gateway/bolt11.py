
# See https://github.com/rustyrussell/lightning-payencode for a more compelte bolt11 decoder with an encoder too

from decimal import Decimal
import re

import bitstring
import secp256k1

from py_ln_gateway.bech32 import bech32_decode, CHARSET
from py_ln_gateway.models import MAX_BOLT11

BTC_TO_MILLISATOSHIS = 10**11

# Bech32 spits out array of 5-bit values.  Shim here.
def u5_to_bitarray(arr):
    ret = bitstring.BitArray()
    for a in arr:
        ret += bitstring.pack("uint:5", a)
    return ret

# Discard trailing bits, convert to bytes.
def trim_to_bytes(barr):
    # Adds a byte if necessary.
    b = barr.tobytes()
    if barr.len % 8 != 0:
        return b[:-1]
    return b

def msatoshi_from_str_amount(amount):
    """ Given a shortened amount, convert it into a decimal
    """
    # BOLT #11:
    # The following `multiplier` letters are defined:
    #
    #* `m` (milli): multiply by 0.001
    #* `u` (micro): multiply by 0.000001
    #* `n` (nano): multiply by 0.000000001
    #* `p` (pico): multiply by 0.000000000001
    units = {
        'p': 10**12,
        'n': 10**9,
        'u': 10**6,
        'm': 10**3,
    }
    unit = str(amount)[-1]
    # BOLT #11:
    # A reader SHOULD fail if `amount` contains a non-digit, or is followed by
    # anything except a `multiplier` in the table above.
    if not re.fullmatch("\d+[pnum]?", str(amount)):
        raise ValueError("Invalid amount '{}'".format(amount))

    if unit in units.keys():
        # TODO optimize the table instead of multiplying by BTC_TO_MILLISATOSHIS here
        return int((BTC_TO_MILLISATOSHIS * Decimal(amount[:-1])) / units[unit])
    else:
        # Convert from btc to millisatoshis
        return int(BTC_TO_MILLISATOSHIS * Decimal(amount))

# Try to pull out tagged data: returns tag, tagged data and remainder.
def pull_tagged(stream):
    tag = stream.read(5).uint
    length = stream.read(5).uint * 32 + stream.read(5).uint
    return (CHARSET[tag], stream.read(length * 5), stream)

def bolt11_decode(bolt11, amount_required=False):
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

    amountstr = hrp[2+m.end():]
    if amountstr == '':
        if amount_required:
            return {'error': "No amount specified in bolt11"}
    else:
        decoded_bolt11['msatoshi'] = msatoshi_from_str_amount(amountstr)

    data = u5_to_bitarray(data);

    # Final signature 65 bytes, split it off.
    if len(data) < 65*8:
        return {'error': "bolt11 too short to contain signature"}
    sigdecoded = data[-65*8:].tobytes()
    data = bitstring.ConstBitStream(data[:-65*8])

    decoded_bolt11['created_at'] = data.read(35).uint

    pubkey = None
    while data.pos != data.len:
        tag, tagdata, data = pull_tagged(data)

        # BOLT #11:
        #
        # A reader MUST skip over unknown fields, an `f` field with unknown
        # `version`, or a `p`, `h`, or `n` field which does not have
        # `data_length` 52, 52, or 53 respectively.
        data_length = len(tagdata) / 5

        if tag == 'x':
            decoded_bolt11['expiry'] = tagdata.uint

        elif tag == 'p':
            if data_length != 52:
                return {'error': 'bolt11: p tag is expected to have legth 52 instead of %s' % data_length}
            decoded_bolt11['payment_hash'] = trim_to_bytes(tagdata).hex()

        elif tag == 'n':
            if data_length != 53:
                continue
            pubkey = secp256k1.PublicKey(flags=secp256k1.ALL_FLAGS)
            pubkey.deserialize(trim_to_bytes(tagdata))

        else:
            # Ignore all other tags
            continue

    if not 'expiry' in decoded_bolt11:
        # BOLT #11: Default is 3600 (1 hour) if not specified.
        decoded_bolt11['expiry'] = 3600

    # BOLT #11:
    #
    # A reader MUST check that the `signature` is valid (see the `n` tagged
    # field specified below).
    if pubkey: # Specified by `n`
        # BOLT #11:
        #
        # A reader MUST use the `n` field to validate the signature instead of
        # performing signature recovery if a valid `n` field is provided.
        signature = pubkey.ecdsa_deserialize_compact(sigdecoded[0:64])
        if not pubkey.ecdsa_verify(bytearray([ord(c) for c in hrp]) + data.tobytes(), signature):
            return {'error': 'bolt11: Invalid signature'}
    else: # Recover pubkey from signature.
        pubkey = secp256k1.PublicKey(flags=secp256k1.ALL_FLAGS)
        signature = pubkey.ecdsa_recoverable_deserialize(sigdecoded[0:64], sigdecoded[64])
        pubkey.public_key = pubkey.ecdsa_recover(bytearray([ord(c) for c in hrp]) + data.tobytes(), signature)

    decoded_bolt11['payee'] = pubkey.serialize().hex()

    return decoded_bolt11
