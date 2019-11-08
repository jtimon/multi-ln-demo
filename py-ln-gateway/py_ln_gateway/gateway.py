
# Example invoice:
# {'payment_hash': 'a1a06ea2fd1240473eb721b7f1b1d306de1b27ea63ed0f42722c69ea62873b46', 'expires_at': 1572696240, 'bolt11': 'lnbca10n1pwmgd3spp55xsxaghazfqyw04hyxmlrvwnqm0pkfl2v0ks7snj93575c588drqdwdveex7m2lvd5xz6twtuc47ar0ta3ksctfde0nzhmzdak8gvf3takxucnrvgcnqm33wpmk6emyxdehqup4wpmngvnhxqu8wefn0p5x56rhvamhs7tgvscrwet4xsmnqet2wsmkken48pekw7r4wsurs7tjdc6hqvmkxeekgur2wcukk7r2vdknjarpxd4h5atwxpjrxvrt0qm8yury895rjdmkdfk8vvm2dpuxxmt2vsukxwr8xe6rqerr0pchj6nhx4ckxutsxgmr2em9w3snqct2dgu8xap4dfjh2wrewqmkzvpnv9kh5utdxgc8xmt8xaun2ctpw5m8zwpewf58z7rrvam8saejvvm8y6psddhx6emsw9jkuvrwwfmhzdmg89n82mfnde6h5urdddcxvmr5x4c82cf4x3arywpnd3shjumsxc6rswfkdd0kgetnvdexjur5d9hkuxqyjw5qcqp277yuhhqs87udwph8a0jf7v5s6j80rgaw9gz6qtq8dz3xyna2yd2xkm4fvaw5hhdn8nv9rjw2suuvcl3hdfrqm8fufu4xsc6s8u6nm7cpsnyucv', 'warning_capacity': 'No channel with a peer that is not a dead end, has sufficient incoming capacity'}

# Example payment result:
# {'id': 2, 'payment_hash': 'a1a06ea2fd1240473eb721b7f1b1d306de1b27ea63ed0f42722c69ea62873b46', 'destination': '02bc1adb03dd2102e4dabfb5554f5a489c9283f3ec663f71ff513045570f576b32', 'msatoshi': 1000, 'amount_msat': 1000msat, 'msatoshi_sent': 1000, 'amount_sent_msat': 1000msat, 'created_at': 1572091440, 'status': 'complete', 'payment_preimage': '2ff6f48168975725a8e7078741ae390f3979df1f52c92ac4ef84a4a494ee25fb', 'bolt11': 'lnbca10n1pwmgd3spp55xsxaghazfqyw04hyxmlrvwnqm0pkfl2v0ks7snj93575c588drqdwdveex7m2lvd5xz6twtuc47ar0ta3ksctfde0nzhmzdak8gvf3takxucnrvgcnqm33wpmk6emyxdehqup4wpmngvnhxqu8wefn0p5x56rhvamhs7tgvscrwet4xsmnqet2wsmkken48pekw7r4wsurs7tjdc6hqvmkxeekgur2wcukk7r2vdknjarpxd4h5atwxpjrxvrt0qm8yury895rjdmkdfk8vvm2dpuxxmt2vsukxwr8xe6rqerr0pchj6nhx4ckxutsxgmr2em9w3snqct2dgu8xap4dfjh2wrewqmkzvpnv9kh5utdxgc8xmt8xaun2ctpw5m8zwpewf58z7rrvam8saejvvm8y6psddhx6emsw9jkuvrwwfmhzdmg89n82mfnde6h5urdddcxvmr5x4c82cf4x3arywpnd3shjumsxc6rswfkdd0kgetnvdexjur5d9hkuxqyjw5qcqp277yuhhqs87udwph8a0jf7v5s6j80rgaw9gz6qtq8dz3xyna2yd2xkm4fvaw5hhdn8nv9rjw2suuvcl3hdfrqm8fufu4xsc6s8u6nm7cpsnyucv'}

from decimal import Decimal
from pprint import pprint
import binascii
import re

from hashlib import sha256

from py_ln_gateway.bech32 import bech32_decode

BIP173_TO_CHAIN_PETNAME = {
    'bcrt': 'regtest',
    'bca': 'chain_1',
    'bcb': 'chain_2',
    'bcc': 'chain_3',
    'bcd': 'chain_4',
    'bce': 'chain_5',
}

def check_hash_preimage(payment_hash, payment_preimage):
    hashed_result = sha256(binascii.unhexlify(payment_preimage)).hexdigest()
    return hashed_result == payment_hash

# Copied from https://github.com/rustyrussell/lightning-payencode
def unshorten_amount(amount):
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
        return Decimal(amount[:-1]) / units[unit]
    else:
        return Decimal(amount)

def check_mandatory(req, required_args, method='method'):
    for arg in required_args:
        if not arg in req:
            return {'error': '%s needs %s field.' % (method, field)}
    return None

def check_unkown_args(req, known_args, method='method'):
    for arg in req:
        if arg not in known_args:
            return {'error': '%s: unkown arg %s.' % (method, arg)}
    return None

class Gateway(object):

    def __init__(self, sibling_nodes):
        # FIX DoS: Don't store pending request forever
        self.prices = {}
        self.sibling_nodes = sibling_nodes
        self.requests_to_be_paid = {}
        self.requests_paid = {}

    def print_state(self):
        print('self.sibling_nodes:')
        pprint(self.sibling_nodes)
        print('self.prices:')
        pprint(self.prices)
        print('self.requests_to_be_paid:')
        pprint(self.requests_to_be_paid)
        print('self.requests_paid:')
        pprint(self.requests_paid)

    def update_price(self, src_chain, dest_chain, price):
        if src_chain not in self.prices:
            self.prices[src_chain] = {}
        self.prices[src_chain][dest_chain] = price

    def update_price_bi(self, src_chain, dest_chain, price):
        self.update_price(src_chain, dest_chain, price)
        self.update_price(dest_chain, src_chain, 1 / price) # Inverse of price for multiplication operation

    def request_dest_payment(self, req):
        required_args = ['bolt11', 'src_chain', 'offer_msats']
        error = check_mandatory(req, required_args, method='request_dest_payment')
        if error: return error
        error = check_unkown_args(req, required_args, method='request_dest_payment')
        if error: return error

        dest_bolt11 = req['bolt11']
        offer_msats = req['offer_msats']
        # FIX change to chain_id (genesis hash) since chain names aren't guaranteed to be unique
        src_chain = req['src_chain']

        if src_chain not in self.sibling_nodes or src_chain not in self.prices:
            return {'error': "gateway doesn't accept payment in chain %s" % src_chain}

        dest_chain_hrp, data = bech32_decode(dest_bolt11)
        if not dest_chain_hrp:
            return {'error': "Bad bech32 checksum for bolt11"}

        if not dest_chain_hrp.startswith('ln'):
            return {'error': "Bad bolt11, hrp does not start with ln"}

        print('dest_chain_hrp', dest_chain_hrp)
        m = re.search("[^\d]+", dest_chain_hrp[2:])
        if not m:
            return {'error': "No chain bip173 name in bolt11"}

        dest_chain_bip173_name = m.group(0)
        amountstr = dest_chain_hrp[2+m.end():]
        if amountstr == '':
            return {'error': "No amount in bolt11"}
        dest_amount_msats = unshorten_amount(amountstr)

        if not dest_chain_bip173_name in BIP173_TO_CHAIN_PETNAME:
            return {'error': "gateway won't pay to chain with bip173 name (hrp) %s" % dest_chain_bip173_name}

        dest_chain = BIP173_TO_CHAIN_PETNAME[dest_chain_bip173_name]

        if (dest_chain not in self.sibling_nodes or
            dest_chain not in self.prices[src_chain] or
            self.prices[src_chain][dest_chain] <= 0):
            return {'error': "gateway won't pay to chain %s" % dest_chain}

        if Decimal(offer_msats) * self.prices[src_chain][dest_chain] < dest_amount_msats:
            return {'error': "Insufficient offer %s" % offer_msats,
                    'suggested_offer_msats': dest_amount_msats / self.prices[src_chain][dest_chain],
            }

        # FIX check that there's actually a route before accepting the request
        label = 'from_%s_to_%s_label' % (src_chain, dest_chain)
        description = 'from_%s_to_%s_bolt11_%s_description' % (src_chain, dest_chain, dest_bolt11)
        src_invoice = self.sibling_nodes[src_chain].invoice(offer_msats, label, description)
        self.requests_to_be_paid[src_invoice['payment_hash']] = {
            'src_chain': src_chain,
            'src_bolt11': src_invoice['bolt11'],
            'src_expires_at': src_invoice['expires_at'],
            'dest_chain': dest_chain,
            'dest_bolt11': dest_bolt11,
        }
        return src_invoice

    def confirm_src_payment(self, req):
        required_args = ['payment_hash', 'payment_preimage']
        error = check_mandatory(req, required_args, method='confirm_src_payment')
        if error: return error
        error = check_unkown_args(req, required_args, method='confirm_src_payment')
        if error: return error

        payment_hash = req['payment_hash']
        payment_preimage = req['payment_preimage']
        if not check_hash_preimage(payment_hash, payment_preimage):
            return {'error': 'Payment preimage does not correspond to the hash.'}

        if payment_hash in self.requests_paid:
            return {
                'error': 'Payment request %s already paid.' % payment_hash,
                'payment': self.requests_paid[payment_hash],
            }

        if payment_hash not in self.requests_to_be_paid:
            return {'error': 'Unkown payment request %s.' % payment_hash}

        to_pay = self.requests_to_be_paid[payment_hash]

        invoices = self.sibling_nodes[to_pay['src_chain']].listinvoices()['invoices']
        found = None
        for invoice in invoices:
            if invoice['payment_hash'] == payment_hash:
                found = invoice
                break

        # The following 2 errors should never occur given the preimage corresponds to the hash, but let's be safe
        if not found:
            return {'error': 'Invoice not found %s.' % payment_hash}

        if found['status'] != 'paid':
            return {'error': 'Invoice not paid yet, current status %s %s.' % (found['status'], payment_hash)}

        # FIX check price one more time to avoid the free option problem?
        # Prices may have been changed from request to confirm call
        try:
            result = self.sibling_nodes[to_pay['dest_chain']].pay(to_pay['dest_bolt11'])
            # TODO This should be a log or go to a database
            self.requests_paid[payment_hash] = {
                'src_chain': to_pay['src_chain'],
                'src_bolt11': to_pay['src_bolt11'],
                'src_expires_at': to_pay['src_expires_at'],
                'dest_chain': to_pay['dest_chain'],
                'dest_bolt11': to_pay['dest_bolt11'],
                'src_payment_hash': payment_hash,
                'src_payment_preimage': payment_preimage,
                'dest_payment_hash': result['payment_hash'],
                'dest_payment_preimage': result['payment_preimage'],
            }
            del self.requests_to_be_paid[payment_hash]
        except Exception as e:
            print(e)
            print(type(e))
            # TODO Save failed requests and hanlde them with refunds or something
            return {
                'error': 'Error paying request.',
                'bolt11': to_pay['dest_bolt11']
            }

        return {
            'payment_hash': result['payment_hash'],
            'payment_preimage': result['payment_preimage'],
        }

def init_gateway(lightningd_map, user_name):
    gateway_sibling_nodes = {}
    for chain_name in lightningd_map:
        if user_name in lightningd_map[chain_name]:
            gateway_sibling_nodes[chain_name] = lightningd_map[chain_name][user_name]
    return Gateway(gateway_sibling_nodes)