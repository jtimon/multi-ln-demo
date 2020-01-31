#!/usr/bin/env python3

if __name__ != '__main__':
    raise ImportError(u"%s may only be run as a script" % __file__)

import binascii
import requests
import sys
import time

from hashlib import sha256

from multiln.utils_demo_bitcoin import (
    btc_generate_all_chains,
    btc_init_bitcoind_global,
    btc_print_block_at_height,
    btc_wait_deamons_start,
    generate_blocks,
    print_balances,
)

from multiln.util_demo_clightning import (
    ln_assert_channels_public,
    ln_assert_channels_state,
    ln_connect_nodes,
    ln_init_global,
    ln_init_info,
    ln_listchannels,
    ln_listfunds,
    ln_listpeers,
    ln_print_info,
    ln_sync_blockheight,
    ln_wait_channels_state,
    ln_wait_deamons_start,
)

from multiln.chains import CHAINS

def check_hash_preimage(payment_hash, payment_preimage):
    hashed_result = sha256(binascii.unhexlify(payment_preimage)).hexdigest()
    return hashed_result == payment_hash

print('This is a demo demonstrating lightning payments across several different regtest chains')
print('USAGE: single parameter containing selected chains separated by commas')

SELECTED_CHAINS = sys.argv[1].split(',')
print('Selected Chains:', SELECTED_CHAINS)

if len(SELECTED_CHAINS) == 0:
    raise AssertionError("No chains selected to run the demo.")

EXAMPLE_CHAIN = SELECTED_CHAINS[0]

CHAINS = {k: CHAINS[k] for k in SELECTED_CHAINS}
N_CHAINS = len(CHAINS)

print('Chains considered (%s):' % N_CHAINS)
print(CHAINS)

GATEWAY_URL = {
    'bob': 'http://bob_gateway:5000',
    'carol': 'http://carol_gateway:6000',
}

BITCOIND = btc_init_bitcoind_global(CHAINS)
LIGHTNINGD = ln_init_global(CHAINS)

# pay an invoice on every chain
def demo_pay_every_chain(lightningd_map):
    if N_CHAINS == 2:
        return

    # A node receives invoices for every other node in the chain and pays it
    for chain_name, ln_daemons in lightningd_map.items():
        for user_name_a, ln_caller_a in ln_daemons.items():
            for user_name_b, ln_caller_b in ln_daemons.items():
                if user_name_a != user_name_b:
                    msatoshi = 1000
                    print('%s receives invoice from %s on chain %s' % (user_name_a, user_name_b, chain_name))
                    desc = '%s_%s_%s' % (user_name_a, user_name_b, chain_name)
                    invoice = ln_caller_b.invoice(msatoshi, '%s_label' % desc, '%s_description' % desc)
                    print(invoice)
                    print('...and pays it...')
                    print(ln_caller_a.pay(invoice['bolt11']))
            break

def demo_2_chains_gateway_payment(lightningd_map, user_name_a, chain_name_a, user_name_gateway, user_name_b, chain_name_b):
    print('--------Running demo_2_chains_gateway_payment()...')
    print('user_name_a = %s' % user_name_a)
    print('chain_name_a = %s' % chain_name_a)
    print('user_name_gateway = %s' % user_name_gateway)
    print('user_name_b = %s' % user_name_b)
    print('chain_name_b = %s' % chain_name_b)

    msatoshi = 1000
    print('%s on chain %s receives invoice for %s msatoshis from %s on chain %s' % (user_name_a, chain_name_a, msatoshi, user_name_b, chain_name_b))
    desc = '%s_%s_%s' % (user_name_a, user_name_b, chain_name_b)
    invoice = lightningd_map[chain_name_b][user_name_b].invoice(msatoshi, '%s_label' % desc, '%s_description' % desc)
    print(invoice)
    print('...and tries to pay it...')
    try:
        print(lightningd_map[chain_name_a][user_name_a].pay(invoice['bolt11']))
    except Exception as e:
        print(e)
        print(type(e))
        print(e.error['message'])
        assert(e.method == 'pay')
        assert(e.error['code'] == 205 # Invoice is for another network
               or e.error['code'] == -32602 # Invalid bolt11: Unknown chain
               or e.error['code'] == 205 # Could not find a route
        )
        assert(e.error['message'] == 'Invoice is for another network %s' % chain_name_b
               or e.error['message'] == 'Invalid bolt11: Unknown chain %s' % CHAINS[chain_name_b]['bip173_name']
               or e.error['message'] == 'Could not find a route'
        )
        assert('bolt11' in e.payload)

    print(requests.get(GATEWAY_URL[user_name_gateway] + "/get_accepted_chains").json())
    print(requests.get(GATEWAY_URL[user_name_gateway] + "/get_prices").json())
    src_invoice = requests.post(GATEWAY_URL[user_name_gateway] + "/request_dest_payment", data={
        'bolt11': invoice['bolt11'],
        'src_chain_ids': [CHAINS[chain_name_a]['id']],
    }).json()
    print("...but since %s can't pay to chain %s, pays the following invoice to %s gateway inc in chain %s instead..." % (user_name_a, chain_name_b, user_name_gateway, chain_name_a))
    print('src_invoice:', src_invoice)
    if 'error' in src_invoice: return

    try:
        src_payment_result = lightningd_map[chain_name_a][user_name_a].pay(src_invoice['bolt11'])
        print('payment succesful:')
        print(src_payment_result)
        print('...and after a successful payment to %s gateway inc, %s calls again with the proof of payment...' % (user_name_gateway, user_name_a))
        gateway_confirm_payment_result = requests.post(GATEWAY_URL[user_name_gateway] + "/confirm_src_payment", data={
            'payment_hash': src_payment_result['payment_hash'],
            'payment_preimage': src_payment_result['payment_preimage'],
        }).json()
        print('...this is what %s gateway inc responds:' % (user_name_gateway))
        print(gateway_confirm_payment_result)
        assert(not 'error' in gateway_confirm_payment_result)
        print('...%s confirms that the payment preimage given corresponds to the original invoice to be paid by %s gateway inc too.' % (user_name_a, user_name_gateway))
        if check_hash_preimage(invoice['payment_hash'], gateway_confirm_payment_result['payment_preimage']):
            print('Preimage corresponds to payment hash')
        else:
            print('Preimage doesn\'t corresponds to payment hash. %s has been scammed by %s' % (user_name_a, user_name_gateway))

    except Exception as e:
        print(e)
        print(type(e))

##################################

btc_wait_deamons_start(BITCOIND)

# Generate and mature the coins in each chain
btc_generate_all_chains(BITCOIND, 101)
print_balances(BITCOIND)
btc_print_block_at_height(BITCOIND, 1)

# lightning-specific things from here
ln_wait_deamons_start(LIGHTNINGD)
LN_INFO = ln_init_info(LIGHTNINGD)
print('LN_INFO:')
print(LN_INFO)

# Send coins to all lightning wallets
for chain_name, ln_daemons in LIGHTNINGD.items():
    rpccaller = BITCOIND[chain_name]
    for user_name, ln_caller in ln_daemons.items():
        print(rpccaller.call('getbalances', {}))
        address = ln_caller.newaddr('p2sh-segwit')['p2sh-segwit']
        txid = rpccaller.call('sendtoaddress', {'address': address, 'amount': 10})
        print('%s %s: sending coins to address %s in lightning wallet (txid: %s)' % (chain_name, user_name, address, txid))
        generate_blocks(rpccaller, chain_name, 1)

ln_sync_blockheight(BITCOIND, LIGHTNINGD, timeout=60 * N_CHAINS, interval=5, label='initial funds on lightningd nodes')
ln_connect_nodes(LIGHTNINGD, LN_INFO)

print_balances(BITCOIND)
ln_print_info(LN_INFO)
ln_listfunds(LIGHTNINGD)
ln_listpeers(LIGHTNINGD)

# A node funds a channel with every other node in the chain
for chain_name, ln_daemons in LIGHTNINGD.items():
    for user_name_a, ln_caller in ln_daemons.items():
        for user_name_b in ln_daemons:
            if user_name_a != user_name_b:
                print('%s funds a channel to %s in chain %s' % (user_name_a, user_name_b, chain_name))
                print(ln_caller.fundchannel(LN_INFO[chain_name][user_name_b]['id'], 10000))
        break

ln_assert_channels_state(LIGHTNINGD, 'CHANNELD_AWAITING_LOCKIN')
ln_assert_channels_public(LIGHTNINGD, False)

# Only one block is required in testnets for a channel to be confirmed
btc_generate_all_chains(BITCOIND, 1)
ln_wait_channels_state(LIGHTNINGD, 'CHANNELD_NORMAL', wait_interval=5)

ln_listchannels(LIGHTNINGD)

demo_pay_every_chain(LIGHTNINGD)

# Alice on regtest pays an invoice to carol on liquid-regtest through gateway bob with nodes on both chains
if N_CHAINS > 1:
    demo_2_chains_gateway_payment(LIGHTNINGD,
                                  user_name_a = 'alice',
                                  chain_name_a = 'regtest',
                                  user_name_gateway = 'bob',
                                  user_name_b = 'carol',
                                  chain_name_b = 'liquid-regtest')

if N_CHAINS > 2:
    # Bob on liquid-regtest pays an invoice to david on chain_3 through gateway carol with nodes on both chains
    demo_2_chains_gateway_payment(LIGHTNINGD,
                                  user_name_a = 'bob',
                                  chain_name_a = 'liquid-regtest',
                                  user_name_gateway = 'carol',
                                  user_name_b = 'david',
                                  chain_name_b = 'chain_3')

# TODO Pay from alice to david using lightning

print('All done for selected chains %s' % SELECTED_CHAINS)
