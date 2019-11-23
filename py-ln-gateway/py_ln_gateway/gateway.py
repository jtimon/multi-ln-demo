
# Example invoice:
# {'payment_hash': 'a1a06ea2fd1240473eb721b7f1b1d306de1b27ea63ed0f42722c69ea62873b46', 'expires_at': 1572696240, 'bolt11': 'lnbca10n1pwmgd3spp55xsxaghazfqyw04hyxmlrvwnqm0pkfl2v0ks7snj93575c588drqdwdveex7m2lvd5xz6twtuc47ar0ta3ksctfde0nzhmzdak8gvf3takxucnrvgcnqm33wpmk6emyxdehqup4wpmngvnhxqu8wefn0p5x56rhvamhs7tgvscrwet4xsmnqet2wsmkken48pekw7r4wsurs7tjdc6hqvmkxeekgur2wcukk7r2vdknjarpxd4h5atwxpjrxvrt0qm8yury895rjdmkdfk8vvm2dpuxxmt2vsukxwr8xe6rqerr0pchj6nhx4ckxutsxgmr2em9w3snqct2dgu8xap4dfjh2wrewqmkzvpnv9kh5utdxgc8xmt8xaun2ctpw5m8zwpewf58z7rrvam8saejvvm8y6psddhx6emsw9jkuvrwwfmhzdmg89n82mfnde6h5urdddcxvmr5x4c82cf4x3arywpnd3shjumsxc6rswfkdd0kgetnvdexjur5d9hkuxqyjw5qcqp277yuhhqs87udwph8a0jf7v5s6j80rgaw9gz6qtq8dz3xyna2yd2xkm4fvaw5hhdn8nv9rjw2suuvcl3hdfrqm8fufu4xsc6s8u6nm7cpsnyucv', 'warning_capacity': 'No channel with a peer that is not a dead end, has sufficient incoming capacity'}

# Example payment result:
# {'id': 2, 'payment_hash': 'a1a06ea2fd1240473eb721b7f1b1d306de1b27ea63ed0f42722c69ea62873b46', 'destination': '02bc1adb03dd2102e4dabfb5554f5a489c9283f3ec663f71ff513045570f576b32', 'msatoshi': 1000, 'amount_msat': 1000msat, 'msatoshi_sent': 1000, 'amount_sent_msat': 1000msat, 'created_at': 1572091440, 'status': 'complete', 'payment_preimage': '2ff6f48168975725a8e7078741ae390f3979df1f52c92ac4ef84a4a494ee25fb', 'bolt11': 'lnbca10n1pwmgd3spp55xsxaghazfqyw04hyxmlrvwnqm0pkfl2v0ks7snj93575c588drqdwdveex7m2lvd5xz6twtuc47ar0ta3ksctfde0nzhmzdak8gvf3takxucnrvgcnqm33wpmk6emyxdehqup4wpmngvnhxqu8wefn0p5x56rhvamhs7tgvscrwet4xsmnqet2wsmkken48pekw7r4wsurs7tjdc6hqvmkxeekgur2wcukk7r2vdknjarpxd4h5atwxpjrxvrt0qm8yury895rjdmkdfk8vvm2dpuxxmt2vsukxwr8xe6rqerr0pchj6nhx4ckxutsxgmr2em9w3snqct2dgu8xap4dfjh2wrewqmkzvpnv9kh5utdxgc8xmt8xaun2ctpw5m8zwpewf58z7rrvam8saejvvm8y6psddhx6emsw9jkuvrwwfmhzdmg89n82mfnde6h5urdddcxvmr5x4c82cf4x3arywpnd3shjumsxc6rswfkdd0kgetnvdexjur5d9hkuxqyjw5qcqp277yuhhqs87udwph8a0jf7v5s6j80rgaw9gz6qtq8dz3xyna2yd2xkm4fvaw5hhdn8nv9rjw2suuvcl3hdfrqm8fufu4xsc6s8u6nm7cpsnyucv'}

# Example decoded dest_invoice:
# {'currency': 'bcb', 'created_at': 1574455201, 'expiry': 604800, 'payee': '0310e6acd171bf63ea5e0fb541082b4cdd9a7bc34aaedc3eeb2b14e8939e073cf4', 'msatoshi': 1000, 'amount_msat': 1000msat, 'description': 'alice_carol_chain_2_description', 'min_final_cltv_expiry': 10, 'payment_hash': '34d771f86c9b17f9f15042f6c387408f8e931022eb30ac3dbed3d972dc742376', 'signature': '304402205021e829da965737470e4be8684c75ec48f1bf0e6762e8eccfe7b6e448da2b8f022008576c29d5453a852df817ca88029f3eaf820b73e1aafc8e505aac32a3a00fd2'}

# Example route:
# {'route': [{'id': '03d34c85a1b9fb3fa67355c2b82cb1c179d1a4819b119035794eb8c839148719de', 'channel': '104x1x0', 'direction': 0, 'msatoshi': 1000, 'amount_msat': 1000msat, 'delay': 9}]}

from decimal import Decimal
from pprint import pprint
import binascii
import json
import re

from hashlib import sha256
from lightning import LightningRpc

from py_ln_gateway import db
from py_ln_gateway.bech32 import bech32_decode
from py_ln_gateway.models import (
    FailedRequest,
    MAX_BOLT11,
    PaidRequest,
    PendingRequest,
    Price,
)

def check_hash_preimage(payment_hash, payment_preimage):
    hashed_result = sha256(binascii.unhexlify(payment_preimage)).hexdigest()
    return hashed_result == payment_hash

MIN_OFFER = 1000

class Gateway(object):

    def __init__(self, nodes_config_path):
        self.sibling_nodes = {}
        with open(nodes_config_path) as json_file:
            data = json.load(json_file)
            # The chain id is the hash of the genesis block
            # REM petname and bip173 are just local settings, others can set them differently
            self.chains_by_bip173 = data['chains_by_bip173']
            for chain_id, node_config in data['nodes'].items():
                print(chain_id, node_config)
                self.sibling_nodes[chain_id] = LightningRpc(node_config)

    def chainparams_from_id(self, chain_id):
        for key, val in self.chains_by_bip173.items():
            if val['id'] == chain_id:
                return val
        return None

    def check_basic(self, req, known_args, required_args, method='check_basic'):
        for arg in req:
            if arg not in known_args:
                return {'error': '%s: unknown arg %s.' % (method, arg)}

        for arg in required_args:
            if arg not in req:
                return {'error': '%s: arg %s is required.' % (method, arg)}

        return None

    def get_accepted_chains(self):
        return {'accepted_chains': list(self.sibling_nodes.keys())}

    def get_prices(self):
        prices = []
        for p in Price.query.all():
            prices.append({
                'src_chain': p.src_chain,
                'dest_chain': p.dest_chain,
                'price': str(p.price),
            })
        return {'prices': prices}

    def request_dest_payment(self, req):
        required_args = ['bolt11', 'src_chain_ids']
        error = self.check_basic(req, required_args, required_args, method='request_dest_payment')
        if error: return error
        print('Received valid req for %s:' % 'request_dest_payment', req)

        dest_bolt11 = req['bolt11']
        if len(dest_bolt11) > MAX_BOLT11:
            return {'error': "Bolt11 invoices above %s in length are rejected" % MAX_BOLT11}

        src_chain_ids = req.getlist('src_chain_ids')
        src_chain_id = None
        for chain_id in src_chain_ids:
            for node_chain_id in self.sibling_nodes.keys():
                if chain_id == node_chain_id:
                    src_chain_id = chain_id
                    break # TODO allow configuring rankings or consult prices instead of simply using the first match found

        if not src_chain_id:
            return {'error': "Offer chains %s not accepted. Accepted chains %s" % (
                str(src_chain_ids), str(list(self.sibling_nodes.keys())))}

        dest_chain_hrp, data = bech32_decode(dest_bolt11)
        if not dest_chain_hrp:
            return {'error': "Bad bech32 checksum for bolt11"}

        if not dest_chain_hrp.startswith('ln'):
            return {'error': "Bad bolt11, hrp does not start with ln"}

        m = re.search("[^\d]+", dest_chain_hrp[2:])
        if not m:
            return {'error': "No chain bip173 name in bolt11"}

        dest_chain_bip173_name = m.group(0)
        if not dest_chain_bip173_name in self.chains_by_bip173:
            return {'error': "gateway won't pay to chain with bip173 name (hrp) %s" % dest_chain_bip173_name}

        dest_chain_id = self.chains_by_bip173[dest_chain_bip173_name]['id']
        if dest_chain_id not in self.sibling_nodes:
            return {'error': "gateway can't pay to chain %s" % dest_chain_id}

        try:
            dest_invoice = self.sibling_nodes[dest_chain_id].decodepay(dest_bolt11)
        except Exception as e:
            return {'error': "Invalid bolt11: Bad bech32 string"}

        if 'msatoshi' not in dest_invoice:
            return {'error': "Invalid bolt11: dest_bolt11 needs to specify an amount"}
        dest_amount_msats = dest_invoice['msatoshi']

        price = Price.query.filter(Price.src_chain == src_chain_id, Price.dest_chain == dest_chain_id).first()
        if not price or price.price == 0:
            return {'error': "gateway won't receive from chain %s to pay to chain %s" % (
                src_chain_id, dest_chain_id)}

        # The gateway imposes a price per chain, take it or leave it
        # You can try another chain or another gateway
        offer_msats = dest_amount_msats * price.price
        if offer_msats < MIN_OFFER:
            return {
                'error': "Insufficient amount",
                'src_chain': src_chain_id,
                'dest_chain': dest_chain_id,
                'dest_amount': str(dest_amount_msats),
                'src_amount': str(offer_msats),
                'src_min_amount': str(MIN_OFFER),
            }

        # Check that there's actually a route before accepting the request
        try:
            risk_factor = 1
            route = self.sibling_nodes[dest_chain_id].getroute(dest_invoice['payee'], dest_amount_msats, risk_factor)
            assert('route' in route)
            print('route:', route['route'])
        except Exception as e:
            return {'error': "No route found to pay dest_bolt11"}

        label = 'from_%s_to_%s_label' % (self.chainparams_from_id(src_chain_id)['petname'],
                                         self.chains_by_bip173[dest_chain_bip173_name]['petname'])
        description = 'from_%s_to_%s_bolt11_%s_description' % (src_chain_id, dest_chain_id, dest_bolt11)
        src_invoice = self.sibling_nodes[src_chain_id].invoice(str(int(offer_msats)), label, description)
        print('src_invoice:')
        pprint(src_invoice)
        if len(src_invoice['bolt11']) > MAX_BOLT11:
            return {'error': "Bolt11 invoices above %s in length are rejected" % MAX_BOLT11}

        db.session.add(PendingRequest(
            src_payment_hash = src_invoice['payment_hash'],
            src_chain = src_chain_id,
            src_bolt11 = src_invoice['bolt11'],
            src_expires_at = src_invoice['expires_at'],
            src_amount = int(offer_msats),
            dest_chain = dest_chain_id,
            dest_bolt11 = dest_bolt11,
            dest_amount = int(dest_amount_msats)
        ))
        db.session.commit()
        return src_invoice

    def check_paid_to_own_node(self, payment_hash, src_chain_id):
        invoices = self.sibling_nodes[src_chain_id].listinvoices()['invoices']
        found = None
        for invoice in invoices:
            if invoice['payment_hash'] == payment_hash:
                found = invoice
                break

        if not found:
            return {'error': 'Invoice not found %s.' % payment_hash}

        if found['status'] != 'paid':
            return {'error': 'Invoice not paid yet, current status %s %s.' % (found['status'], payment_hash)}

        return None

    def confirm_src_payment(self, req):
        required_args = ['payment_hash', 'payment_preimage']
        error = self.check_basic(req, required_args, required_args, method='confirm_src_payment')
        if error: return error
        print('Received valid req for %s:' % 'confirm_src_payment', req)

        payment_hash = req['payment_hash']
        payment_preimage = req['payment_preimage']
        if not check_hash_preimage(payment_hash, payment_preimage):
            return {'error': 'Payment preimage does not correspond to the hash.'}

        paid_request = PaidRequest.query.get(payment_hash)
        if paid_request:
            return {
                'error': 'Payment request %s already paid.' % payment_hash,
                'dest_payment_hash': paid_request.dest_payment_hash,
                'dest_payment_preimage': paid_request.dest_payment_preimage,
            }

        failed_request = FailedRequest.query.get(payment_hash)
        if failed_request:
            return {
                'error': 'Payment request %s already failed. Please contact customer support.' % payment_hash,
            }

        pending_request = PendingRequest.query.get(payment_hash)
        if not pending_request:
            return {'error': 'Unkown payment request %s.' % payment_hash}

        # This should never fail given the preimage corresponds to the hash, but let's be safe
        error = self.check_paid_to_own_node(payment_hash, pending_request.src_chain)
        if error: return error

        # Prices may have been changed from request to confirm call
        # Check the price one more time to mitigate the free option problem. If it fails because of this, a refund is required too.
        price = Price.query.filter(Price.src_chain == pending_request.src_chain, Price.dest_chain == pending_request.dest_chain).first()
        if not price or price.price == 0:
            return {'error': "gateway won't receive from chain %s to pay to chain %s" % (
                pending_request.src_chain, pending_request.dest_chain)}

        src_current_offer = pending_request.dest_amount * price.price
        if Decimal(pending_request.src_amount) < src_current_offer:
            error = "The offered price is no longer accepted."
            db.session.add(FailedRequest(
                error = error,
                src_payment_hash = payment_hash,
                src_payment_preimage = payment_preimage,
                src_chain = pending_request.src_chain,
                src_bolt11 = pending_request.src_bolt11,
                src_expires_at = pending_request.src_expires_at,
                dest_chain = pending_request.dest_chain,
                dest_bolt11 = pending_request.dest_bolt11,
            ))
            # Delete from pending_requests when failing too
            db.session.delete(pending_request)
            db.session.commit()
            return {
                'error': error,
                'src_payment_hash': payment_hash,
                'src_current_offer': src_current_offer,
                'dest_bolt11': pending_request.dest_bolt11,
            }

        try:
            result = self.sibling_nodes[pending_request.dest_chain].pay(pending_request.dest_bolt11)
            db.session.add(PaidRequest(
                src_payment_hash = payment_hash,
                src_chain = pending_request.src_chain,
                src_bolt11 = pending_request.src_bolt11,
                src_expires_at = pending_request.src_expires_at,
                src_payment_preimage = payment_preimage,
                dest_chain = pending_request.dest_chain,
                dest_bolt11 = pending_request.dest_bolt11,
                dest_payment_hash = result['payment_hash'],
                dest_payment_preimage = result['payment_preimage'],
            ))
            db.session.delete(pending_request)
            db.session.commit()
        except Exception as e:
            print(type(e))
            print(e)
            # TODO handle failed requests with refunds or something
            # We could refund by opening a channel with some initial funds back to the customer,
            # but then we need to have the node id on the initial request.
            # Alternatively we can accept a refund invoice in this call.
            db.session.add(FailedRequest(
                error = str(e),
                src_payment_hash = payment_hash,
                src_payment_preimage = payment_preimage,
                src_chain = pending_request.src_chain,
                src_bolt11 = pending_request.src_bolt11,
                src_expires_at = pending_request.src_expires_at,
                dest_chain = pending_request.dest_chain,
                dest_bolt11 = pending_request.dest_bolt11,
            ))
            # Delete from pending_requests when failing too
            db.session.delete(pending_request)
            db.session.commit()
            return {
                'error': 'Error paying request.',
                'src_payment_hash': payment_hash,
                'dest_bolt11': pending_request.dest_bolt11,
            }

        return {
            'payment_hash': result['payment_hash'],
            'payment_preimage': result['payment_preimage'],
        }
