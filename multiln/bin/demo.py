#!/usr/bin/env python3

if __name__ != '__main__':
    raise ImportError(u"%s may only be run as a script" % __file__)

import sys
import time

from multiln.utils_demo_bitcoin import (
    btc_connect_nodes,
    btc_generate_all_chains,
    btc_init_bitcoind_global,
    generate_blocks,
    get_p2p_port,
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
    ln_wait_deamons_start,
    ln_wait_initial_funds,
)

print('This is a demo demonstrating lightning payments across several different regtest chains')

SELECTED_CHAINS = sys.argv[1:]
print('Selected Chains:', SELECTED_CHAINS)

if len(SELECTED_CHAINS) == 0:
    raise AssertionError("No chains selected to run the demo.")

EXAMPLE_CHAIN = SELECTED_CHAINS[0]

CHAINS = {
    'regtest': {
        'port_decimal': 1,
        'users': ['alice', 'bob'],
        'main_user': 'alice',
    },

    'chain_1': {
        'port_decimal': 4,
        'users': ['alice', 'bob'],
        'main_user': 'alice',
    },

    'chain_2': {
        'port_decimal': 5,
        'users': ['bob', 'carol'],
        'main_user': 'bob',
    },

    'chain_3': {
        'port_decimal': 6,
        'users': ['carol', 'david'],
        'main_user': 'carol',
    },

    'chain_4': {
        'port_decimal': 7,
        'users': ['david', 'ezra'],
        'main_user': 'david',
    },

    'chain_5': {
        'port_decimal': 8,
        'users': ['ezra', 'fiona'],
        'main_user': 'ezra',
    },
}
CHAINS = {k: CHAINS[k] for k in SELECTED_CHAINS}
N_CHAINS = len(CHAINS)

print('Chains considered (%s):', N_CHAINS)
print(CHAINS)

BITCOIND = btc_init_bitcoind_global(CHAINS)
LIGHTNINGD = ln_init_global(CHAINS)

# Try to pay an invoice from carol on chain_2 from alice on chain_1
def demo_2_chains_fail(lightningd_map):
    if N_CHAINS < 2:
        return

    print('--------Running demo_2_chains_fail()...')
    # TODO Select the users in a more dynamic way
    user_name_a = 'alice'
    chain_name_a = 'chain_1'
    user_name_b = 'carol'
    chain_name_b = 'chain_2'

    msatoshi = 1000
    print('%s on chain %s receives invoice for %s msatoshis from %s on chain %s' % (user_name_a, chain_name_a, msatoshi, user_name_b, chain_name_b))
    desc = '%s_%s_%s' % (user_name_a, user_name_b, chain_name)
    invoice = lightningd_map[chain_name_b][user_name_b].invoice(msatoshi, '%s_label' % desc, '%s_description' % desc)
    print(invoice)
    print('...and tries to pay it...')
    try:
        print(lightningd_map[chain_name_a][user_name_a].pay(invoice['bolt11']))
    except Exception as e:
        print(e)
        print(type(e))
        assert(e.method == 'pay')
        assert(e.error['code'] == 205)
        assert(e.error['message'] == 'Could not find a route')
        assert('bolt11' in e.payload)

##################################

print('--------Wait for %s daemons to start and connect (%s seconds)' % (N_CHAINS, N_CHAINS * 5))
time.sleep(N_CHAINS * 5)
btc_connect_nodes(CHAINS, BITCOIND)

# Let's make sure everyone generates some coins in the chains they participate in
for chain_name, chain_daemons in BITCOIND.items():
    for rpccaller in chain_daemons.values():
        generate_blocks(BITCOIND, rpccaller, chain_name, 1)

# Let's mature the coins in each chain
btc_generate_all_chains(BITCOIND, 100)

print_balances(BITCOIND)

print('--------Let\'s try an on-chain payment first on chain %s' % EXAMPLE_CHAIN)

# Alice can pay bob directly on EXAMPLE_CHAIN
bob_address = BITCOIND[EXAMPLE_CHAIN]['bob'].call('getnewaddress', {})
txid = BITCOIND[EXAMPLE_CHAIN]['alice'].call('sendtoaddress', {'address': bob_address, 'amount': 1})
print('Alice can pay bob directly on EXAMPLE_CHAIN (txid: %s)' % txid)
generate_blocks(BITCOIND, BITCOIND[EXAMPLE_CHAIN]['alice'], EXAMPLE_CHAIN, 1)
print_balances(BITCOIND)

# lightning-specific things from here
ln_wait_deamons_start(LIGHTNINGD)
LN_INFO = ln_init_info(LIGHTNINGD)
print('LN_INFO:')
print(LN_INFO)

# Send coins to all lightning wallets
for chain_name, chain_daemons in BITCOIND.items():
    for user_name, rpccaller in chain_daemons.items():
        print(rpccaller.call('getbalances', {}))
        address = LIGHTNINGD[chain_name][user_name].newaddr('p2sh-segwit')['p2sh-segwit']
        txid = rpccaller.call('sendtoaddress', {'address': address, 'amount': 10})
        print('%s %s: sending coins to address %s in lightning wallet (txid: %s)' % (chain_name, user_name, address, txid))
        generate_blocks(BITCOIND, rpccaller, chain_name, 1)

ln_wait_initial_funds(LIGHTNINGD)

ln_connect_nodes(LIGHTNINGD, LN_INFO)

print_balances(BITCOIND)
ln_print_info(LN_INFO)
ln_listfunds(LIGHTNINGD)
ln_listpeers(LIGHTNINGD)
ln_listchannels(LIGHTNINGD)

# A node funds a channel with every other node in the chain
for chain_name, ln_daemons in LIGHTNINGD.items():
    for user_name_a, ln_caller in ln_daemons.items():
        for user_name_b in ln_daemons:
            if user_name_a != user_name_b:
                print('%s funds a channel to %s in chain %s' % (user_name_a, user_name_b, chain_name))
                print(ln_caller.fundchannel(LN_INFO[chain_name][user_name_b]['id'], 10000))
        break

ln_listfunds(LIGHTNINGD)
ln_listpeers(LIGHTNINGD)
ln_listchannels(LIGHTNINGD)

ln_assert_channels_state(LIGHTNINGD, 'CHANNELD_AWAITING_LOCKIN')

# Only one block is required in testnets for a channel to be confirmed
btc_generate_all_chains(BITCOIND, 1)
print('--------Wait for %s clightning daemons to sync to confirm the channels (%s seconds)' % (N_CHAINS, 30))
time.sleep(30)
ln_assert_channels_state(LIGHTNINGD, 'CHANNELD_NORMAL')
ln_assert_channels_public(LIGHTNINGD, False)

ln_listchannels(LIGHTNINGD)
# After 6 confirmations it becomes public
# btc_generate_all_chains(BITCOIND, 5)
# time.sleep(30)
# ln_listchannels(LIGHTNINGD)
# ln_assert_channels_public(LIGHTNINGD, True)

# A node receives invoices for every other node in the chain and pays it
for chain_name, ln_daemons in LIGHTNINGD.items():
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


# Try to pay an invoice from carol on chain_2 from alice on chain_1
demo_2_chains_fail(LIGHTNINGD)

# TODO Pay from alice to fiona using lightning

# import json
# print(json.dumps(LIGHTNINGD[EXAMPLE_CHAIN]['alice'].help(), indent=4, sort_keys=True))

print('All done for selected chains %s' % SELECTED_CHAINS)
