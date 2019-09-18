#!/usr/bin/env python3

if __name__ != '__main__':
    raise ImportError(u"%s may only be run as a script" % __file__)

import sys
import time

from lightning import LightningRpc
from multiln.rpccaller import RpcCaller
from multiln.bitcoin_test_utils import (
    connect_nodes,
    sync_blocks,
)

print('This is a demo demonstrating lightning payments across several different regtest chains')

SELECTED_CHAINS = sys.argv[1:]
print('Selected Chains:', SELECTED_CHAINS)

if len(SELECTED_CHAINS) == 0:
    raise AssertionError("No chains selected to run the demo.")

EXAMPLE_CHAIN = SELECTED_CHAINS[0]

CHAINS = {
    'regtest': {
        'port_decimal': 1
    },
    'chain_1': {
        'port_decimal': 4
    },
    'chain_2': {
        'port_decimal': 5
    },
    'chain_3': {
        'port_decimal': 6
    },
    'chain_4': {
        'port_decimal': 7
    },
    'chain_5': {
        'port_decimal': 8
    },
}
CHAINS = {k: CHAINS[k] for k in SELECTED_CHAINS}

USERS_PER_CHAIN = {
    'regtest': ['alice', 'bob'],
    'chain_1': ['alice', 'bob'],
    'chain_2': ['bob', 'carol'],
    'chain_3': ['carol', 'david'],
    'chain_4': ['david', 'ezra'],
    'chain_5': ['ezra', 'fiona'],
}
USERS_PER_CHAIN = {k: USERS_PER_CHAIN[k] for k in SELECTED_CHAINS}

MAIN_USER_PER_CHAIN = {
    'regtest': 'alice',
    'chain_1': 'alice',
    'chain_2': 'bob',
    'chain_3': 'carol',
    'chain_4': 'david',
    'chain_5': 'ezra',
}
MAIN_USER_PER_CHAIN = {k: MAIN_USER_PER_CHAIN[k] for k in SELECTED_CHAINS}

print('Chains considered:', CHAINS)
print('Users considered:', USERS_PER_CHAIN)

def get_p2p_decimal_1(chain_name, user_name):
    # TODO This only scales to 2 nodes per chain
    if MAIN_USER_PER_CHAIN[chain_name] == user_name:
        return '5'
    else:
        return '6'

def get_p2p_port(chain_name, user_name):
    return '18%s%s6' % (
        # TODO This only scales to 2 nodes per chain
        get_p2p_decimal_1(chain_name, user_name),
        CHAINS[chain_name]['port_decimal'],
    )

def btc_init_bitcoind_global():
    to_return = {}
    for chain_name in CHAINS:
        to_return[chain_name] = {}
        for user_name in USERS_PER_CHAIN[chain_name]:
            port_chain_user = '18%s%s5' % (
                get_p2p_decimal_1(chain_name, user_name),
                CHAINS[chain_name]['port_decimal'],
            )
            to_return[chain_name][user_name] = RpcCaller(
                '0.0.0.0:%s' % port_chain_user,
                'user%s' % port_chain_user,
                'password%s' % port_chain_user,
            )
    return to_return

def ln_init_global():
    to_return = {}
    for chain_name in CHAINS:
        to_return[chain_name] = {}
        for user_name in USERS_PER_CHAIN[chain_name]:
            to_return[chain_name][user_name] = LightningRpc('/wd/daemon-data/%s_%s/lightning-rpc' % (user_name, chain_name))
    return to_return

BITCOIND = btc_init_bitcoind_global()
LIGHTNINGD = ln_init_global()

# Connect all nodes of the same chain with each other
def btc_connect_nodes():
    for chain_name, chain_daemons in BITCOIND.items():
        for user_name_a, rpccaller in chain_daemons.items():
            for user_name_b in chain_daemons:
                if user_name_a != user_name_b:
                    connect_nodes(BITCOIND[chain_name][user_name_a], '127.0.0.1:%s' % get_p2p_port(chain_name, user_name_b))

def generate_blocks(rpccaller, chain_name, nblocks):
    address = rpccaller.call('getnewaddress', {})
    block_hashes = rpccaller.call('generatetoaddress', {'nblocks': nblocks, 'address': address})
    print('Generated %s %s blocks:' % (nblocks, chain_name))
    # print(block_hashes)
    sync_blocks(BITCOIND[chain_name].values())

def btc_generate_all_chains(nblocks):
    for chain_name, chain_daemons in BITCOIND.items():
        # Any daemon for each chain will do
        rpccaller = next(iter(chain_daemons.values()))
        generate_blocks(rpccaller, chain_name, nblocks)

def print_balances():
    for chain_name, chain_daemons in BITCOIND.items():
        for user_name, rpccaller in chain_daemons.items():
            print(chain_name, user_name, rpccaller.call('getbalances', {}))

LN_INFO = {}

def ln_update_info():
    for chain_name, ln_daemons in LIGHTNINGD.items():
        LN_INFO[chain_name] = {}
        for user_name, ln_caller in ln_daemons.items():
            LN_INFO[chain_name][user_name] = ln_caller.getinfo()
    print('LN_INFO:')
    print(LN_INFO)

def ln_print_info():
    for chain_name, ln_users in LN_INFO.items():
        for user_name, info in ln_users.items():
            print(chain_name, user_name, info)

def ln_listfunds():
    for chain_name, ln_daemons in LIGHTNINGD.items():
        for user_name, ln_caller in ln_daemons.items():
            print(chain_name, user_name, ln_caller.listfunds())

def ln_listchannels():
    for chain_name, ln_daemons in LIGHTNINGD.items():
        for user_name, ln_caller in ln_daemons.items():
            print(chain_name, user_name, ln_caller.listchannels())

def ln_listpeers():
    for chain_name, ln_daemons in LIGHTNINGD.items():
        for user_name, ln_caller in ln_daemons.items():
            print(chain_name, user_name, ln_caller.listpeers())

def ln_assert_channels_state(state):
    for chain_name, ln_daemons in LIGHTNINGD.items():
        for user_name, ln_caller in ln_daemons.items():
            for peer in ln_caller.listpeers()['peers']:
                for channel in peer['channels']:
                    if state != channel['state']:
                        raise AssertionError('%s %s: Expected state %s but got state %s' % (
                            chain_name,
                            user_name,
                            state,
                            channel['state'],
                        ))

def ln_assert_channels_public(expected_public=True):
    for chain_name, ln_daemons in LIGHTNINGD.items():
        for user_name, ln_caller in ln_daemons.items():
            for channel in ln_caller.listchannels()['channels']:
                if expected_public != channel['public']:
                    raise AssertionError('%s %s: Expected channel.public to be %s, but it was not' % (
                        chain_name,
                        user_name,
                        expected_public,
                    ))


# Connect all lightning nodes in the same chain to each other
def ln_connect_nodes():
    for chain_name, ln_daemons in LIGHTNINGD.items():
        for user_name_a, rpccaller in LIGHTNINGD[chain_name].items():
            for user_name_b, info_b in LN_INFO[chain_name].items():
                if user_name_a != user_name_b:
                    print('Connecting %s to %s in chain %s, port %s id %s' % (
                        user_name_a, user_name_b, chain_name, info_b['binding'][0]['port'], info_b['id']))
                    rpccaller.connect(info_b['id'], host='0.0.0.0', port=info_b['binding'][0]['port'])

# wait for everyone to have some onchain funds on every chain they're in
def ln_wait_initial_funds():
    for chain_name, chain_daemons in LIGHTNINGD.items():
        for user_name, rpccaller in chain_daemons.items():
            while len(LIGHTNINGD[chain_name][user_name].listfunds()['outputs']) == 0:
                print('Waiting for user %s initial funds on chain %s (linghtning node)' % (user_name, chain_name))
                time.sleep(1)

##################################

# Wait for daemons to start
time.sleep(5)

btc_connect_nodes()

# Let's make sure everyone generates some coins in the chains they participate in
for chain_name, chain_daemons in BITCOIND.items():
    for rpccaller in chain_daemons.values():
        generate_blocks(rpccaller, chain_name, 1)

# Let's mature the coins in each chain
btc_generate_all_chains(100)

print_balances()

# Alice can pay bob directly on EXAMPLE_CHAIN
bob_address = BITCOIND[EXAMPLE_CHAIN]['bob'].call('getnewaddress', {})
txid = BITCOIND[EXAMPLE_CHAIN]['alice'].call('sendtoaddress', {'address': bob_address, 'amount': 1})
print('Alice can pay bob directly on EXAMPLE_CHAIN (txid: %s)' % txid)
generate_blocks(BITCOIND[EXAMPLE_CHAIN]['alice'], EXAMPLE_CHAIN, 1)
print_balances()

# lightning-specific things from here
time.sleep(10)
ln_update_info()

# Send coins to all lightning wallets
for chain_name, chain_daemons in BITCOIND.items():
    for user_name, rpccaller in chain_daemons.items():
        print(rpccaller.call('getbalances', {}))
        address = LIGHTNINGD[chain_name][user_name].newaddr('p2sh-segwit')['p2sh-segwit']
        txid = rpccaller.call('sendtoaddress', {'address': address, 'amount': 10})
        print('%s %s: sending coins to address %s in lightning wallet (txid: %s)' % (chain_name, user_name, address, txid))
        generate_blocks(rpccaller, chain_name, 1)

ln_wait_initial_funds()

ln_connect_nodes()

print_balances()
ln_print_info()
ln_listfunds()
ln_listpeers()
ln_listchannels()

# A node funds a channel with every other node in the chain
for chain_name, ln_daemons in LIGHTNINGD.items():
    for user_name_a, ln_caller in ln_daemons.items():
        for user_name_b in ln_daemons:
            if user_name_a != user_name_b:
                print('%s funds a channel to %s in chain %s' % (user_name_a, user_name_b, chain_name))
                print(ln_caller.fundchannel(LN_INFO[chain_name][user_name_b]['id'], 10000))
        break

ln_listfunds()
ln_listpeers()
ln_listchannels()

ln_assert_channels_state('CHANNELD_AWAITING_LOCKIN')

# Only one block is required in testnets for a channel to be confirmed
btc_generate_all_chains(1)
time.sleep(30)
ln_assert_channels_state('CHANNELD_NORMAL')
ln_assert_channels_public(False)

ln_listchannels()
# After 6 confirmations it becomes public
# btc_generate_all_chains(5)
# time.sleep(30)
# ln_listchannels()
# ln_assert_channels_public(True)

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

# TODO Pay from alice to fiona using lightning

# import json
# print(json.dumps(LIGHTNINGD[EXAMPLE_CHAIN]['alice'].help(), indent=4, sort_keys=True))

print('All done for selected chains %s' % SELECTED_CHAINS)
