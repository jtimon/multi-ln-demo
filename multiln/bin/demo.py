#!/usr/bin/env python3

if __name__ != '__main__':
    raise ImportError(u"%s may only be run as a script" % __file__)

import time
from lightning import LightningRpc
from multiln.rpccaller import RpcCaller
from multiln.bitcoin_test_utils import (
    connect_nodes,
    sync_blocks,
)

print('This is a demo demonstrating lightning payments across several different regtest chains')

CHAINS = {
    'chain_1': {
        'port_decimal': 4
    },
    'chain_2': {
        'port_decimal': 5
    },
    # 'chain_3': {
    #     'port_decimal': 6
    # },
    # 'chain_4': {
    #     'port_decimal': 7
    # },
    # 'chain_5': {
    #     'port_decimal': 8
    # },
}

USERS_PER_CHAIN = {
    'chain_1': ['alice', 'bob'],
    'chain_2': ['bob', 'carol'],
    'chain_3': ['carol', 'david'],
    'chain_4': ['david', 'ezra'],
    'chain_5': ['ezra', 'fiona'],
}

MAIN_USER_PER_CHAIN = {
    'chain_1': 'alice',
    'chain_2': 'bob',
    'chain_3': 'carol',
    'chain_4': 'david',
    'chain_5': 'ezra',
}

print('Chains considered:', CHAINS)
print('Users considered:', USERS_PER_CHAIN)

def select_chains(chains, by_chain_dict):
    to_return = {}
    for chain_name, chain_items in by_chain_dict.items():
        if chain_name in chains:
            to_return[chain_name] = chain_items
    return to_return

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
    print('Generated %s blocks:' % chain_name)
    print(block_hashes)
    sync_blocks(BITCOIND[chain_name].values())

def print_balances():
    for chain_name, chain_daemons in BITCOIND.items():
        for user_name, rpccaller in chain_daemons.items():
            print(chain_name, user_name, rpccaller.call('getbalances', {}))

LN_INFO = {}

def ln_update_info():
    for chain_name, ln_daemons in LIGHTNINGD.items():
        LN_INFO[chain_name] = {}
        for user_name, rpccaller in ln_daemons.items():
            LN_INFO[chain_name][user_name] = LIGHTNINGD[chain_name][user_name].getinfo()

def ln_print_info():
    for chain_name, ln_users in LN_INFO.items():
        for user_name, info in ln_users.items():
            print(chain_name, user_name, info)

def ln_print_funds():
    for chain_name, ln_daemons in LIGHTNINGD.items():
        for user_name, rpccaller in ln_daemons.items():
            print(chain_name, user_name, LIGHTNINGD[chain_name][user_name].listfunds())

# Connect all lightning nodes in the same chain to each other
def ln_connect_nodes():
    for chain_name, ln_daemons in LIGHTNINGD.items():
        for user_name_a, rpccaller in LIGHTNINGD[chain_name].items():
            for user_name_b, info_b in LN_INFO[chain_name].items():
                if user_name_a != user_name_b:
                    rpccaller.connect(info_b['id'], host='0.0.0.0', port=info_b['binding'][0]['port'])

##################################

# Wait for daemons to start
time.sleep(5)

btc_connect_nodes()
ln_update_info()

# Let's make sure everyone generates some coins in the chains they participate in
for chain_name, chain_daemons in BITCOIND.items():
    for rpccaller in chain_daemons.values():
        generate_blocks(rpccaller, chain_name, 1)

# Let's mature the coins in each chain
for chain_daemons in BITCOIND.values():
    # Any daemon for each chain will do
    rpccaller = next(iter(chain_daemons.values()))
    generate_blocks(rpccaller, chain_name, 100)

print_balances()

# Alice can pay bob directly on chain_1
bob_address = BITCOIND['chain_1']['bob'].call('getnewaddress', {})
txid = BITCOIND['chain_1']['alice'].call('sendtoaddress', {'address': bob_address, 'amount': 1})
print('Alice can pay bob directly on chain_1 (txid: %s)' % txid)
generate_blocks(BITCOIND['chain_1']['alice'], 'chain_1', 1)
print_balances()

# Send coins to all lightning wallets
for chain_name, chain_daemons in BITCOIND.items():
    for user_name, rpccaller in chain_daemons.items():
        print(rpccaller.call('getbalances', {}))
        address = LIGHTNINGD['chain_1']['alice'].newaddr('p2sh-segwit')['address']
        txid = rpccaller.call('sendtoaddress', {'address': address, 'amount': 10})
        print('sending coins to address %s in lightning wallet (txid: %s)' % (address, txid))
        generate_blocks(rpccaller, chain_name, 1)
print_balances()

ln_print_info()
ln_print_funds()

# FIX Cryptographic handshake: peer closed connection (wrong key?)
ln_connect_nodes()

# TODO Create lightning channels

# TODO Pay from alice to fiona using lightning

print('All done. Exiting in 5 seconds...')
time.sleep(5)
