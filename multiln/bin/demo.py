#!/usr/bin/env python3

if __name__ != '__main__':
    raise ImportError(u"%s may only be run as a script" % __file__)

import requests
import sys
import time

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

print('This is a demo demonstrating lightning payments across several different regtest chains')
print('USAGE: single parameter containing a natural number of hops (from 0 to 2)')

N_HOPS = int(sys.argv[1])
SELECTED_CHAINS = ["regtest"]
if N_HOPS > 0:
    SELECTED_CHAINS.append("liquid-regtest")

print('Selected hops:', N_HOPS)

CHAINS = {k: CHAINS[k] for k in SELECTED_CHAINS}
print('Chains considered (%s):' % len(CHAINS))
print(CHAINS)

GATEWAY_URL = {
    'bob': 'http://bob_gateway:5000',
    'carol': 'http://carol_gateway:6000',
}

BITCOIND = btc_init_bitcoind_global(CHAINS)
LIGHTNINGD = ln_init_global(CHAINS)

def demo_fundchannel(lightningd_map, ln_info, chain_name, user_name_a, user_name_b, amount):
    print('%s funds a channel to %s in chain %s' % (user_name_a, user_name_b, chain_name))
    print(lightningd_map[chain_name][user_name_a].fundchannel(ln_info[chain_name][user_name_b]['id'], amount))

# A node receives invoices for every other node in the chain and pays it
def demo_1_chain_payment(lightningd_map, chain_name, payer, payee, msatoshi):
    print('%s receives invoice from %s on chain %s' % (payer, payee, chain_name))
    desc = '%s_%s_%s' % (payer, payee, chain_name)
    invoice = lightningd_map[chain_name][payee].invoice(msatoshi, '%s_label' % desc, '%s_description' % desc)
    print(invoice)
    print('...and pays it...')
    print(lightningd_map[chain_name][payer].pay(invoice['bolt11']))

def demo_2_chains_gateway_payment(lightningd_map, user_name_a, chain_name_a, user_name_gateway, user_name_b, chain_name_b):
    print('--------Running demo_2_chains_gateway_payment()...')
    print('user_name_a = %s' % user_name_a)
    print('chain_name_a = %s' % chain_name_a)
    print('user_name_gateway = %s' % user_name_gateway)
    print('user_name_b = %s' % user_name_b)
    print('chain_name_b = %s' % chain_name_b)

    print(requests.get(GATEWAY_URL[user_name_gateway] + "/get_accepted_chains").json())
    print(requests.get(GATEWAY_URL[user_name_gateway] + "/get_prices").json())

    msatoshi = 1000
    print('%s on chain %s receives invoice for %s msatoshis from %s on chain %s' % (user_name_a, chain_name_a, msatoshi, user_name_b, chain_name_b))
    desc = '%s_%s_%s' % (user_name_a, user_name_b, chain_name_b)
    invoice = lightningd_map[chain_name_b][user_name_b].invoice(msatoshi, '%s_label' % desc, '%s_description' % desc)
    print('invoice', invoice)
    gatepay_result = lightningd_map[chain_name_a][user_name_a].gatepay(invoice['bolt11'])
    print("...but since %s can't pay to chain %s, it tries to pay %s gateway inc in chain %s instead..." % (user_name_a, chain_name_b, user_name_gateway, chain_name_a))
    print('...and after a successful payment to %s gateway inc, %s calls again with the proof of payment...' % (user_name_gateway, user_name_a))
    print('...this is what %s gateway inc responds:' % (user_name_gateway))
    print('...%s confirms that the payment preimage given corresponds to the original invoice to be paid by %s gateway inc too.' % (user_name_a, user_name_gateway))
    print('gatepay_result', gatepay_result)
    assert('error' not in gatepay_result)

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

ln_sync_blockheight(BITCOIND, LIGHTNINGD, timeout=60 * (N_HOPS + 1), interval=5, label='initial funds on lightningd nodes')
ln_connect_nodes(LIGHTNINGD, LN_INFO)

print_balances(BITCOIND)
ln_print_info(LN_INFO)
ln_listfunds(LIGHTNINGD)
ln_listpeers(LIGHTNINGD)

demo_fundchannel(LIGHTNINGD, LN_INFO, "regtest", "alice", "bob", 10000)
if N_HOPS > 0:
    demo_fundchannel(LIGHTNINGD, LN_INFO, "liquid-regtest", "bob", "carol", 10000)
if N_HOPS > 1:
    demo_fundchannel(LIGHTNINGD, LN_INFO, "regtest", "carol", "david", 10000)

ln_assert_channels_state(LIGHTNINGD, 'CHANNELD_AWAITING_LOCKIN')
ln_assert_channels_public(LIGHTNINGD, False)

# Only one block is required in testnets for a channel to be confirmed
btc_generate_all_chains(BITCOIND, 1)
ln_wait_channels_state(LIGHTNINGD, 'CHANNELD_NORMAL', wait_interval=5)

ln_listchannels(LIGHTNINGD)

# Pay an invoice on every chain
demo_1_chain_payment(LIGHTNINGD, "regtest", "alice", "bob", 1000)
if N_HOPS > 0:
    demo_1_chain_payment(LIGHTNINGD, "liquid-regtest", "bob", "carol", 1000)
if N_HOPS > 1:
    demo_1_chain_payment(LIGHTNINGD, "regtest", "carol", "david", 1000)

# Alice on regtest pays an invoice to carol on liquid-regtest through gateway bob with nodes on both chains
if N_HOPS > 0:
    demo_2_chains_gateway_payment(LIGHTNINGD,
                                  user_name_a = 'alice',
                                  chain_name_a = 'regtest',
                                  user_name_gateway = 'bob',
                                  user_name_b = 'carol',
                                  chain_name_b = 'liquid-regtest')

if N_HOPS > 1:
    # Bob on liquid-regtest pays an invoice to david on regtest through gateway carol with nodes on both chains
    demo_2_chains_gateway_payment(LIGHTNINGD,
                                  user_name_a = 'bob',
                                  chain_name_a = 'liquid-regtest',
                                  user_name_gateway = 'carol',
                                  user_name_b = 'david',
                                  chain_name_b = 'regtest')

    # Alice on regtest pays an invoice to david on regtest through gateway bob with nodes in regtest and liquid-regtest
    # Gateway bob needs to call gateway carol to be able to pay to regtest
    demo_2_chains_gateway_payment(LIGHTNINGD,
                                  user_name_a = 'alice',
                                  chain_name_a = 'regtest',
                                  user_name_gateway = 'bob',
                                  user_name_b = 'david',
                                  chain_name_b = 'regtest')

print('All done for %s hops. Used chains %s' % (N_HOPS, SELECTED_CHAINS))
