
# Example invoice:
# {'payment_hash': 'a1a06ea2fd1240473eb721b7f1b1d306de1b27ea63ed0f42722c69ea62873b46', 'expires_at': 1572696240, 'bolt11': 'lnbca10n1pwmgd3spp55xsxaghazfqyw04hyxmlrvwnqm0pkfl2v0ks7snj93575c588drqdwdveex7m2lvd5xz6twtuc47ar0ta3ksctfde0nzhmzdak8gvf3takxucnrvgcnqm33wpmk6emyxdehqup4wpmngvnhxqu8wefn0p5x56rhvamhs7tgvscrwet4xsmnqet2wsmkken48pekw7r4wsurs7tjdc6hqvmkxeekgur2wcukk7r2vdknjarpxd4h5atwxpjrxvrt0qm8yury895rjdmkdfk8vvm2dpuxxmt2vsukxwr8xe6rqerr0pchj6nhx4ckxutsxgmr2em9w3snqct2dgu8xap4dfjh2wrewqmkzvpnv9kh5utdxgc8xmt8xaun2ctpw5m8zwpewf58z7rrvam8saejvvm8y6psddhx6emsw9jkuvrwwfmhzdmg89n82mfnde6h5urdddcxvmr5x4c82cf4x3arywpnd3shjumsxc6rswfkdd0kgetnvdexjur5d9hkuxqyjw5qcqp277yuhhqs87udwph8a0jf7v5s6j80rgaw9gz6qtq8dz3xyna2yd2xkm4fvaw5hhdn8nv9rjw2suuvcl3hdfrqm8fufu4xsc6s8u6nm7cpsnyucv', 'warning_capacity': 'No channel with a peer that is not a dead end, has sufficient incoming capacity'}

# Example payment result:
# {'id': 2, 'payment_hash': 'a1a06ea2fd1240473eb721b7f1b1d306de1b27ea63ed0f42722c69ea62873b46', 'destination': '02bc1adb03dd2102e4dabfb5554f5a489c9283f3ec663f71ff513045570f576b32', 'msatoshi': 1000, 'amount_msat': 1000msat, 'msatoshi_sent': 1000, 'amount_sent_msat': 1000msat, 'created_at': 1572091440, 'status': 'complete', 'payment_preimage': '2ff6f48168975725a8e7078741ae390f3979df1f52c92ac4ef84a4a494ee25fb', 'bolt11': 'lnbca10n1pwmgd3spp55xsxaghazfqyw04hyxmlrvwnqm0pkfl2v0ks7snj93575c588drqdwdveex7m2lvd5xz6twtuc47ar0ta3ksctfde0nzhmzdak8gvf3takxucnrvgcnqm33wpmk6emyxdehqup4wpmngvnhxqu8wefn0p5x56rhvamhs7tgvscrwet4xsmnqet2wsmkken48pekw7r4wsurs7tjdc6hqvmkxeekgur2wcukk7r2vdknjarpxd4h5atwxpjrxvrt0qm8yury895rjdmkdfk8vvm2dpuxxmt2vsukxwr8xe6rqerr0pchj6nhx4ckxutsxgmr2em9w3snqct2dgu8xap4dfjh2wrewqmkzvpnv9kh5utdxgc8xmt8xaun2ctpw5m8zwpewf58z7rrvam8saejvvm8y6psddhx6emsw9jkuvrwwfmhzdmg89n82mfnde6h5urdddcxvmr5x4c82cf4x3arywpnd3shjumsxc6rswfkdd0kgetnvdexjur5d9hkuxqyjw5qcqp277yuhhqs87udwph8a0jf7v5s6j80rgaw9gz6qtq8dz3xyna2yd2xkm4fvaw5hhdn8nv9rjw2suuvcl3hdfrqm8fufu4xsc6s8u6nm7cpsnyucv'}

# Example decoded dest_decoded_bolt11:
# {'currency': 'bcb', 'created_at': 1574455201, 'expiry': 604800, 'payee': '0310e6acd171bf63ea5e0fb541082b4cdd9a7bc34aaedc3eeb2b14e8939e073cf4', 'msatoshi': 1000, 'amount_msat': 1000msat, 'description': 'alice_carol_liquid_regtest_description', 'min_final_cltv_expiry': 10, 'payment_hash': '34d771f86c9b17f9f15042f6c387408f8e931022eb30ac3dbed3d972dc742376', 'signature': '304402205021e829da965737470e4be8684c75ec48f1bf0e6762e8eccfe7b6e448da2b8f022008576c29d5453a852df817ca88029f3eaf820b73e1aafc8e505aac32a3a00fd2'}

# Example route:
# {'route': [{'id': '03d34c85a1b9fb3fa67355c2b82cb1c179d1a4819b119035794eb8c839148719de', 'channel': '104x1x0', 'direction': 0, 'msatoshi': 1000, 'amount_msat': 1000msat, 'delay': 9}]}

from datetime import datetime
from decimal import Decimal
from pprint import pprint
import json
import requests

from hashlib import sha256
from pyln.client import LightningRpc

from py_ln_gateway.db import db_session
from py_ln_gateway.bolt11 import bolt11_decode
from py_ln_gateway.models import (
    FailedRequest,
    MAX_BOLT11,
    PaidRequest,
    PendingRequest,
    Price,
)

REFUND_MSG = 'Please contact customer support to get a refund.'
MIN_OFFER = 1000

def check_hash_preimage(payment_hash, payment_preimage):
    hashed_result = sha256(bytes.fromhex(payment_preimage)).hexdigest()
    return hashed_result == payment_hash

def is_with_error(result):
    return isinstance(result, dict) and 'error' in result

def save_pending_request(src_invoice, dest_decoded_bolt11, dest_bolt11,
                         other_gw_decoded_bolt11=None, other_gw_bolt11=None, other_url=None):
    pending_request = PendingRequest(
        src_payment_hash = src_invoice['payment_hash'],
        src_chain = src_invoice['chain_id'],
        src_bolt11 = src_invoice['bolt11'],
        src_expires_at = datetime.utcfromtimestamp(src_invoice['expires_at']),
        src_amount = int(src_invoice['msatoshi']),
        dest_payment_hash = dest_decoded_bolt11['payment_hash'],
        dest_chain = dest_decoded_bolt11['chain_id'],
        dest_bolt11 = dest_bolt11,
        dest_expires_at = datetime.utcfromtimestamp(dest_decoded_bolt11['created_at'] + dest_decoded_bolt11['expiry']),
        dest_amount = int(dest_decoded_bolt11['msatoshi'])
    )
    if other_gw_decoded_bolt11:
        pending_request.other_gw_payment_hash = other_gw_decoded_bolt11['payment_hash']
        pending_request.other_gw_url = other_url
        pending_request.other_gw_chain = other_gw_decoded_bolt11['chain_id']
        pending_request.other_gw_bolt11 = other_gw_bolt11
        pending_request.other_gw_expires_at = datetime.utcfromtimestamp(other_gw_decoded_bolt11['created_at'] + other_gw_decoded_bolt11['expiry'])
        pending_request.other_gw_amount = int(other_gw_decoded_bolt11['msatoshi'])

    db_session.add(pending_request)
    db_session.commit()

def save_failed_request(error, pending_request, src_payment_preimage, other_gw_payment_preimage=None):
    # TODO handle failed requests with refunds or something
    # We could refund by opening a channel with some initial funds back to the customer,
    # but then we need to have the node id on the initial request.
    # Alternatively we can accept a refund invoice in this call.
    db_session.add(FailedRequest(
        src_payment_hash = pending_request.src_payment_hash,
        error = error,
        src_payment_preimage = src_payment_preimage,
        other_gw_payment_preimage = other_gw_payment_preimage,
        src_chain = pending_request.src_chain,
        src_bolt11 = pending_request.src_bolt11,
        src_expires_at = pending_request.src_expires_at,
        src_amount = pending_request.src_amount,
        dest_payment_hash = pending_request.dest_payment_hash,
        dest_chain = pending_request.dest_chain,
        dest_bolt11 = pending_request.dest_bolt11,
        dest_expires_at = pending_request.dest_expires_at,
        dest_amount = pending_request.dest_amount,
        other_gw_url = pending_request.other_gw_url,
        other_gw_chain = pending_request.other_gw_chain,
        other_gw_bolt11 = pending_request.other_gw_bolt11,
        other_gw_expires_at = pending_request.other_gw_expires_at,
        other_gw_amount = pending_request.other_gw_amount,
    ))
    # Delete from pending_requests when failing too
    db_session.delete(pending_request)
    db_session.commit()

def save_paid_request(pending_request, src_payment_preimage, dest_payment_preimage, other_gw_payment_preimage):
    db_session.add(PaidRequest(
        src_payment_hash = pending_request.src_payment_hash,
        src_payment_preimage = src_payment_preimage,
        dest_payment_preimage = dest_payment_preimage,
        src_chain = pending_request.src_chain,
        src_bolt11 = pending_request.src_bolt11,
        src_expires_at = pending_request.src_expires_at,
        dest_chain = pending_request.dest_chain,
        dest_bolt11 = pending_request.dest_bolt11,
        dest_expires_at = pending_request.dest_expires_at,
        dest_payment_hash = pending_request.dest_payment_hash,
        other_gw_payment_hash = pending_request.other_gw_payment_hash,
        other_gw_payment_preimage = other_gw_payment_preimage,
        other_gw_url = pending_request.other_gw_url,
        other_gw_chain = pending_request.other_gw_chain,
        other_gw_bolt11 = pending_request.other_gw_bolt11,
        other_gw_expires_at = pending_request.other_gw_expires_at,
    ))
    db_session.delete(pending_request)
    db_session.commit()

def sanitize_response_request_dest_payment(response):
    return {
        'bolt11': response['bolt11'],
        'chain_id': response['chain_id'],
    }

class Gateway(object):

    def __init__(self, nodes_config_path):
        self.sibling_nodes = {}
        with open(nodes_config_path) as json_file:
            data = json.load(json_file)
            self.invoices_expiry = data['invoices_expiry']
            # The chain id is the hash of the genesis block
            # REM petname and bip173 are just local settings, others can set them differently
            self.chains_by_bip173 = data['chains_by_bip173']
            for chain_id, node_config in data['nodes'].items():
                print(chain_id, node_config)
                self.sibling_nodes[chain_id] = LightningRpc(node_config)
            self.other_gateways = data['other_gateways']

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

    def _choose_src_chain(self, src_chain_ids):
        src_chain_id = None
        # TODO allow configuring rankings or consult prices instead of simply choosing the first match found
        for chain_id in src_chain_ids:
            for node_chain_id in self.sibling_nodes.keys():
                if chain_id == node_chain_id:
                    src_chain_id = chain_id
                    break
        return src_chain_id

    # Add chain_id field to bolt11_decode if known, or return error
    def _bolt11_decode(self, bolt11):
        decoded_bolt11 = bolt11_decode(bolt11, amount_required=True)
        if is_with_error(decoded_bolt11):
            return decoded_bolt11

        dest_chain_bip173_name = decoded_bolt11['currency']
        if not dest_chain_bip173_name in self.chains_by_bip173:
            return {'error': "gateway won't pay to unknown chain with bip173 currency name (hrp) %s" % dest_chain_bip173_name}
        decoded_bolt11['chain_id'] = self.chains_by_bip173[dest_chain_bip173_name]['id']

        return decoded_bolt11

    # Check that there's actually a route before accepting the request
    def _check_route(self, dest_chain_id, payee, amount_msats, risk_factor=1):
        try:
            route = self.sibling_nodes[dest_chain_id].getroute(payee, amount_msats, risk_factor)
            pprint(route)
            return 'route' in route
        except Exception as e:
            print(e)
            return False

    def _calculate_src_invoice(self, src_chain_id, dest_decoded_bolt11):
        dest_chain_id = dest_decoded_bolt11['chain_id']
        price = Price.query.get('%s:%s' % (src_chain_id, dest_chain_id))
        if not price or price.price == 0:
            return {'error': "gateway won't receive from chain %s to pay to chain %s" % (
                src_chain_id, dest_chain_id)}

        # The gateway imposes a price per chain, take it or leave it
        # You can try another chain or another gateway
        offer_msatoshi = dest_decoded_bolt11['msatoshi'] * price.price
        if offer_msatoshi < MIN_OFFER:
            return {
                'error': "Insufficient amount",
                'src_chain': src_chain_id,
                'dest_chain': dest_chain_id,
                'dest_amount': str(dest_decoded_bolt11['msatoshi']),
                'src_amount': str(offer_msatoshi),
                'src_min_amount': str(MIN_OFFER),
            }

        label = 'from_%s_to_%s_label_%s' % (self.chainparams_from_id(src_chain_id)['petname'],
                                            self.chainparams_from_id(dest_chain_id)['petname'],
                                            dest_decoded_bolt11['payment_hash'])
        description = 'from_%s_to_%s_bolt11_%s_description' % (src_chain_id, dest_chain_id, dest_decoded_bolt11['payment_hash'])
        src_invoice = self.sibling_nodes[src_chain_id].invoice(str(int(offer_msatoshi)), label, description, expiry=self.invoices_expiry)
        if not 'msatoshi' in src_invoice:
            src_invoice['msatoshi'] = int(offer_msatoshi)
        print('src_invoice:')
        pprint(src_invoice)
        if len(src_invoice['bolt11']) > MAX_BOLT11:
            return {'error': "Bolt11 invoices above %s in length are rejected" % MAX_BOLT11}

        src_invoice['chain_id'] = src_chain_id
        return src_invoice

    def _other_gateway_pays(self, dest_bolt11, src_chain_id, dest_decoded_bolt11):
        dest_chain_id = dest_decoded_bolt11['chain_id']
        for other_url, supported_chains in self.other_gateways.items():
            if dest_chain_id not in supported_chains:
                continue

            result = self._other_gateway_attempt(dest_bolt11, src_chain_id, dest_decoded_bolt11, other_url)
            if is_with_error(result):
                print('Error returned by other gateway %s: (chain id %s)' % (other_url, dest_chain_id))
                pprint(result)
            else:
                return result

        return {'error': "No route found to pay bolt11 %s" % dest_bolt11}

    def _other_gateway_attempt(self, dest_bolt11, src_chain_id, dest_decoded_bolt11, other_url):
        dest_chain_id = dest_decoded_bolt11['chain_id']
        other_gw_invoice = requests.post(other_url + "/request_dest_payment", data={
            'bolt11': dest_bolt11,
            'src_chain_ids': list(self.sibling_nodes.keys()),
        }).json()
        if is_with_error(other_gw_invoice):
            return other_gw_invoice

        other_gw_bolt11 = other_gw_invoice['bolt11']
        other_gw_decoded_bolt11 = self._bolt11_decode(other_gw_bolt11)
        if is_with_error(other_gw_decoded_bolt11):
            return other_gw_decoded_bolt11
        other_gw_chain_id = other_gw_decoded_bolt11['chain_id']

        if other_gw_chain_id not in self.sibling_nodes:
            return {'error': 'other gateway demands payment in a chain we don\'t support (chain id: %s)' % other_gw_chain_id}

        # When another gateway pays, make sure we can be paid before checking a route
        src_invoice = self._calculate_src_invoice(src_chain_id, other_gw_decoded_bolt11)
        if is_with_error(src_invoice):
            return src_invoice

        if not self._check_route(other_gw_chain_id, other_gw_decoded_bolt11['payee'], other_gw_decoded_bolt11['msatoshi']):
            return {'error': "No route found to pay other_gw_bolt11 %s" % other_gw_bolt11}

        save_pending_request(src_invoice, dest_decoded_bolt11, dest_bolt11, other_gw_decoded_bolt11, other_gw_bolt11, other_url)
        return sanitize_response_request_dest_payment(src_invoice)

    def get_accepted_chains(self):
        return {'accepted_chains': list(self.sibling_nodes.keys())}

    def get_prices(self):
        prices = []
        for p in Price.query.all():
            splitted = p.src_dest.split(':')
            assert(len(splitted) == 2)
            prices.append({
                'src_chain': splitted[0],
                'dest_chain': splitted[1],
                'price': str(p.price),
            })
        return {'prices': prices}

    def request_dest_payment(self, req):
        required_args = ['bolt11', 'src_chain_ids']
        error = self.check_basic(req, required_args, required_args, method='request_dest_payment')
        if error: return error
        print('Received valid req for %s:' % 'request_dest_payment', req)

        src_chain_id = self._choose_src_chain(req.getlist('src_chain_ids'))
        if not src_chain_id:
            return {'error': "Offered chains not accepted. Accepted chains %s" % (
                str(list(self.sibling_nodes.keys())))}

        dest_bolt11 = req['bolt11']
        dest_decoded_bolt11 = self._bolt11_decode(dest_bolt11)
        if is_with_error(dest_decoded_bolt11):
            return dest_decoded_bolt11
        dest_chain_id = dest_decoded_bolt11['chain_id']

        if dest_chain_id not in self.sibling_nodes:
            print("gateway can't pay to chain %s, trying with another gateway" % dest_chain_id)
            return self._other_gateway_pays(dest_bolt11, src_chain_id, dest_decoded_bolt11)

        # When we can't find a route ourselves, try other gateway before calculating src_invoice
        if not self._check_route(dest_chain_id, dest_decoded_bolt11['payee'], dest_decoded_bolt11['msatoshi']):
            print("No route found to pay dest_bolt11 %s, trying with another gateway" % dest_bolt11)
            return self._other_gateway_pays(dest_bolt11, src_chain_id, dest_decoded_bolt11)

        src_invoice = self._calculate_src_invoice(src_chain_id, dest_decoded_bolt11)
        if is_with_error(src_invoice):
            return src_invoice

        save_pending_request(src_invoice, dest_decoded_bolt11, dest_bolt11)
        return sanitize_response_request_dest_payment(src_invoice)

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
                'error': 'Payment request %s already failed. %s' % (payment_hash, REFUND_MSG),
            }

        pending_request = PendingRequest.query.get(payment_hash)
        if not pending_request:
            return {'error': 'Unkown payment request %s.' % payment_hash}

        # This should never fail given the preimage corresponds to the hash, but let's be safe
        error = self.check_paid_to_own_node(payment_hash, pending_request.src_chain)
        if error: return error

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
        price = Price.query.get('%s:%s' % (pending_request.src_chain, to_pay_chain))
        if not price or price.price == 0:
            return {'error': "gateway won't receive from chain %s to pay to chain %s" % (
                pending_request.src_chain, pending_request.dest_chain)}

        src_current_offer = to_pay_amount * price.price
        if Decimal(pending_request.src_amount) < src_current_offer:
            error_msg = 'The offered price for payment request %s is no longer accepted. %s' % (payment_hash, REFUND_MSG)
            save_failed_request(error_msg, pending_request, payment_preimage)
            return {
                'error': error_msg,
                'src_payment_hash': payment_hash,
                'src_current_offer': src_current_offer,
                'dest_bolt11': pending_request.dest_bolt11,
            }

        try:
            result = self.sibling_nodes[to_pay_chain].pay(to_pay_bolt11)

            if not result['payment_hash'] == to_pay_payment_hash:
                print('WARNING: This should never happen if our own lightning nodes are to be trusted')
                save_failed_request('Payment pending payment_hash does not correspond to the paid hash', pending_request, payment_preimage)
                return {'error': 'Payment request %s failed. %s' % (payment_hash, REFUND_MSG)}

            if not check_hash_preimage(result['payment_hash'], result['payment_preimage']):
                print('WARNING: This should never happen if our own lightning nodes are to be trusted')
                save_failed_request('Payment preimage does not correspond to the hash', pending_request, payment_preimage)
                return {'error': 'Payment request %s failed. %s' % (payment_hash, REFUND_MSG)}

            if pending_request.other_gw_chain:
                other_gw_confirm_payment_result = {'error': 'placeholder error'}
                other_gw_payment_hash = result['payment_hash']
                other_gw_payment_preimage = result['payment_preimage']
                attempts = 0
                while attempts < 5 and ('error' in other_gw_confirm_payment_result
                    or not 'payment_hash' in other_gw_confirm_payment_result
                    or not 'payment_preimage' in other_gw_confirm_payment_result
                    or not check_hash_preimage(other_gw_confirm_payment_result['payment_hash'],
                                               other_gw_confirm_payment_result['payment_preimage'])
                ):
                    other_gw_confirm_payment_result = requests.post(pending_request.other_gw_url + "/confirm_src_payment", data={
                        'payment_hash': other_gw_payment_hash,
                        'payment_preimage': other_gw_payment_preimage,
                    }).json()
                    attempts = attempts + 1

                if ('error' in other_gw_confirm_payment_result
                    or not 'payment_hash' in other_gw_confirm_payment_result
                    or not 'payment_preimage' in other_gw_confirm_payment_result
                    or other_gw_confirm_payment_result['payment_hash'] != pending_request.dest_payment_hash
                    or not check_hash_preimage(pending_request.dest_payment_hash,
                                               other_gw_confirm_payment_result['payment_preimage'])
                ):
                    print('EXPENSIVE ERROR: REM: Don\'t rely on gateway %s anymore and ask for refunds' % pending_request.other_gw_url)
                    pprint(other_gw_confirm_payment_result)
                    save_failed_request('gateway %s is unreliable' % pending_request.other_gw_url,
                                        pending_request, src_payment_preimage,
                                        other_gw_payment_preimage=other_gw_payment_preimage)
                    return {'error': 'Payment request %s failed. %s' % (payment_hash, REFUND_MSG)}

                dest_payment_preimage = other_gw_confirm_payment_result['payment_preimage']
            else:
                dest_payment_preimage = result['payment_preimage']
                other_gw_payment_preimage = None

            save_paid_request(pending_request, payment_preimage, dest_payment_preimage, other_gw_payment_preimage)
        except Exception as e:
            print(type(e))
            print(e)
            save_failed_request(str(e), pending_request, payment_preimage)
            return {'error': 'Payment request %s failed. %s' % (payment_hash, REFUND_MSG)}

        return {
            'payment_hash': pending_request.dest_payment_hash,
            'payment_preimage': dest_payment_preimage,
        }
