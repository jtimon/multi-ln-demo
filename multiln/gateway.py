
# Example invoice:
# {'payment_hash': 'a1a06ea2fd1240473eb721b7f1b1d306de1b27ea63ed0f42722c69ea62873b46', 'expires_at': 1572696240, 'bolt11': 'lnbca10n1pwmgd3spp55xsxaghazfqyw04hyxmlrvwnqm0pkfl2v0ks7snj93575c588drqdwdveex7m2lvd5xz6twtuc47ar0ta3ksctfde0nzhmzdak8gvf3takxucnrvgcnqm33wpmk6emyxdehqup4wpmngvnhxqu8wefn0p5x56rhvamhs7tgvscrwet4xsmnqet2wsmkken48pekw7r4wsurs7tjdc6hqvmkxeekgur2wcukk7r2vdknjarpxd4h5atwxpjrxvrt0qm8yury895rjdmkdfk8vvm2dpuxxmt2vsukxwr8xe6rqerr0pchj6nhx4ckxutsxgmr2em9w3snqct2dgu8xap4dfjh2wrewqmkzvpnv9kh5utdxgc8xmt8xaun2ctpw5m8zwpewf58z7rrvam8saejvvm8y6psddhx6emsw9jkuvrwwfmhzdmg89n82mfnde6h5urdddcxvmr5x4c82cf4x3arywpnd3shjumsxc6rswfkdd0kgetnvdexjur5d9hkuxqyjw5qcqp277yuhhqs87udwph8a0jf7v5s6j80rgaw9gz6qtq8dz3xyna2yd2xkm4fvaw5hhdn8nv9rjw2suuvcl3hdfrqm8fufu4xsc6s8u6nm7cpsnyucv', 'warning_capacity': 'No channel with a peer that is not a dead end, has sufficient incoming capacity'}

# Example payment result:
# {'id': 2, 'payment_hash': 'a1a06ea2fd1240473eb721b7f1b1d306de1b27ea63ed0f42722c69ea62873b46', 'destination': '02bc1adb03dd2102e4dabfb5554f5a489c9283f3ec663f71ff513045570f576b32', 'msatoshi': 1000, 'amount_msat': 1000msat, 'msatoshi_sent': 1000, 'amount_sent_msat': 1000msat, 'created_at': 1572091440, 'status': 'complete', 'payment_preimage': '2ff6f48168975725a8e7078741ae390f3979df1f52c92ac4ef84a4a494ee25fb', 'bolt11': 'lnbca10n1pwmgd3spp55xsxaghazfqyw04hyxmlrvwnqm0pkfl2v0ks7snj93575c588drqdwdveex7m2lvd5xz6twtuc47ar0ta3ksctfde0nzhmzdak8gvf3takxucnrvgcnqm33wpmk6emyxdehqup4wpmngvnhxqu8wefn0p5x56rhvamhs7tgvscrwet4xsmnqet2wsmkken48pekw7r4wsurs7tjdc6hqvmkxeekgur2wcukk7r2vdknjarpxd4h5atwxpjrxvrt0qm8yury895rjdmkdfk8vvm2dpuxxmt2vsukxwr8xe6rqerr0pchj6nhx4ckxutsxgmr2em9w3snqct2dgu8xap4dfjh2wrewqmkzvpnv9kh5utdxgc8xmt8xaun2ctpw5m8zwpewf58z7rrvam8saejvvm8y6psddhx6emsw9jkuvrwwfmhzdmg89n82mfnde6h5urdddcxvmr5x4c82cf4x3arywpnd3shjumsxc6rswfkdd0kgetnvdexjur5d9hkuxqyjw5qcqp277yuhhqs87udwph8a0jf7v5s6j80rgaw9gz6qtq8dz3xyna2yd2xkm4fvaw5hhdn8nv9rjw2suuvcl3hdfrqm8fufu4xsc6s8u6nm7cpsnyucv'}

class Gateway(object):

    def __init__(self, sibling_nodes):
        self.prices = {}
        self.sibling_nodes = sibling_nodes
        self.requests_to_be_paid = {}
        self.requests_paid = {}

    def update_price(self, src_chain, dest_chain, price):
        if src_chain not in self.prices:
            self.prices[src_chain] = {}
        self.prices[src_chain][dest_chain] = price

    def update_price_bi(self, src_chain, dest_chain, price):
        self.update_price(src_chain, dest_chain, price)
        self.update_price(dest_chain, src_chain, 1 / price) # Inverse of price for multiplication operation

    def request_payment(self, req):
        dest_bolt11 = req['bolt11']
        offer_msats = req['offer_msats']
        # FIX change to chain_id (genesis hash) since chain names aren't guaranteed to be unique
        src_chain = req['src_chain']
        dest_amount_msats = req['amount_msats']
        # FIX decode the amount from the req['bolt11'], the caller can lie
        dest_chain = req['dest_chain']

        if src_chain not in self.sibling_nodes or src_chain not in self.prices:
            return {'error': "gateway doesn't accept payment in chain %s" % src_chain}

        if (dest_chain not in self.sibling_nodes or
            dest_chain not in self.prices[src_chain] or
            self.prices[src_chain][dest_chain] <= 0):
            return {'error': "gateway won't pay to chain %s" % dest_chain}

        if offer_msats * self.prices[src_chain][dest_chain] < dest_amount_msats:
            return {'error': "Insufficient offer %s" % offer_msats,
                    'suggested_offer_msats': dest_amount_msats / self.prices[src_chain][dest_chain],
            }

        label = 'from_%s_to_%s_label' % (src_chain, dest_chain)
        description = 'from_%s_to_%s_bolt11_%s_description' % (src_chain, dest_chain, dest_bolt11)
        src_invoice = self.sibling_nodes[src_chain].invoice(offer_msats, label, description)
        self.requests_to_be_paid[src_invoice['payment_hash']] = {
            'src_invoice': src_invoice,
            'dest_bolt11': dest_bolt11,
            'dest_chain': dest_chain,
        }
        return src_invoice

    def confirm_request_payment_payment(self, req):
        payment_hash = req['payment_hash']
        if payment_hash in self.requests_paid:
            return {
                'error': 'Payment request %s already paid.' % payment_hash,
                'payment': self.requests_paid[payment_hash],
            }

        if payment_hash not in self.requests_to_be_paid:
            return {'error': 'Unkown payment request %s.' % payment_hash}

        # TODO the gateway should check if the invoice was already paid before paying his
        to_pay = self.requests_to_be_paid[payment_hash]
        try:
            result = self.sibling_nodes[to_pay['dest_chain']].pay(to_pay['dest_bolt11'])
            self.requests_paid[payment_hash] = {
                'request': self.requests_to_be_paid[payment_hash],
                'src_payment': req,
                'dest_payment': result
            }
            del self.requests_to_be_paid[payment_hash]
        except Exception as e:
            print(e)
            print(type(e))
            return {
                'error': 'Error paying request.',
                'bolt11': to_pay['dest_bolt11']
            }

        return result

def init_gateway(lightningd_map, user_name):
    gateway_sibling_nodes = {}
    for chain_name in lightningd_map:
        if user_name in lightningd_map[chain_name]:
            gateway_sibling_nodes[chain_name] = lightningd_map[chain_name][user_name]
    return Gateway(gateway_sibling_nodes)
