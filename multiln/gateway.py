
class Gateway(object):

    def __init__(self, sibling_nodes):
        self.sibling_nodes = sibling_nodes

    def request_payment(self, req):
        dest_bolt11 = req['bolt11']
        offer_msats = req['offer_msats']
        # FIX change to chain_id (genesis hash) since chain names aren't guaranteed to be unique
        src_chain = req['src_chain']
        dest_amount_msats = req['amount_msats']
        # FIX decode the amount from the req['bolt11'], the caller can lie
        dest_chain = req['src_chain']

        if src_chain not in self.sibling_nodes:
            return {'error': "gateway doesn't accept payment in chain %s" % src_chain}

        if dest_chain not in self.sibling_nodes:
            return {'error': "gateway can't pay to chain %s" % dest_chain}

        # TODO implement some pricing mechanism, always assuming 1:1 for now
        if offer_msats < dest_amount_msats:
            return {'error': "Insufficient offer %s" % offer_msats,
                    'suggested_offer_msats': dest_amount_msats,
            }


        label = 'from_%s_to_%s_label' % (src_chain, dest_chain)
        description = 'from_%s_to_%s_bolt11_%s_description' % (src_chain, dest_chain, dest_bolt11)
        src_invoice = self.sibling_nodes[src_chain].invoice(offer_msats, label, description)
        return src_invoice
        # return {'bolt11': src_invoice['bolt11']}

    def confirm_request_payment_payment(self, req):
        return {'error': 'This service requires Bob Gateway scam premium. Please, login.'}

    def confirmed_request_status(self, req):
        return {'error': 'This service requires Bob Gateway scam premium. Please, login.'}

def init_gateway(lightningd_map, user_name):
    gateway_sibling_nodes = {}
    for chain_name in lightningd_map:
        gateway_sibling_nodes[chain_name] = lightningd_map[chain_name][user_name]
    return Gateway(gateway_sibling_nodes)
