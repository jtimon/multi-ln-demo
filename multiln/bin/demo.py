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

CHAINS = [
    'chain_1',
    'chain_2',
    # 'chain_3',
    # 'chain_4',
    # 'chain_5',
]
USERS = ['alice', 'bob', 'carol', 'david', 'ezra', 'fiona']

print('Chains considered:', CHAINS)
print('Users considered:', USERS)

def select_chains(chains, by_chain_dict):
    to_return = {}
    for chain_name, chain_items in by_chain_dict.items():
        if chain_name in chains:
            to_return[chain_name] = chain_items
    return to_return

# TODO do this in a better way
P2P_PORTS = {
    'chain_1': {
        'alice': '18546',
        'bob': '18646',
    },
    'chain_2': {
        'bob': '18556',
        'carol': '18656',
    },
    'chain_3': {
        'carol': '18566',
        'david': '18666',
    },
    'chain_4': {
        'david': '18576',
        'ezra': '18676',
    },
    'chain_5': {
        'ezra': '18586',
        'fiona': '18686',
    },
}
P2P_PORTS = select_chains(CHAINS, P2P_PORTS)

def get_p2p_port(chain_name, user_name):
    return P2P_PORTS[chain_name][user_name]

# TODO do this in a better way
BITCOIND = {
    'chain_1': {
        'alice': RpcCaller('0.0.0.0:18545', 'user18545', 'password18545'),
        'bob': RpcCaller('0.0.0.0:18645', 'user18645', 'password18645'),
    },
    'chain_2': {
        'bob': RpcCaller('0.0.0.0:18555', 'user18555', 'password18555'),
        'carol': RpcCaller('0.0.0.0:18655', 'user18655', 'password18655'),
    },
    'chain_3': {
        'carol': RpcCaller('0.0.0.0:18565', 'user18565', 'password18565'),
        'david': RpcCaller('0.0.0.0:18665', 'user18665', 'password18665'),
    },
    'chain_4': {
        'david': RpcCaller('0.0.0.0:18575', 'user18575', 'password18575'),
        'ezra': RpcCaller('0.0.0.0:18675', 'user18675', 'password18675'),
    },
    'chain_5': {
        'ezra': RpcCaller('0.0.0.0:18585', 'user18585', 'password18585'),
        'fiona': RpcCaller('0.0.0.0:18685', 'user18685', 'password18685'),
    },
}
BITCOIND = select_chains(CHAINS, BITCOIND)

# TODO do this in a better way
LIGHTNINGD = {
    'chain_1': {
        'alice': LightningRpc('/wd/daemon-data/alice_chain_1/lightning-rpc'),
        'bob': LightningRpc('/wd/daemon-data/bob_chain_1/lightning-rpc'),
    },
    'chain_2': {
        'bob': LightningRpc('/wd/daemon-data/bob_chain_2/lightning-rpc'),
        'carol': LightningRpc('/wd/daemon-data/carol_chain_2/lightning-rpc'),
    },
    'chain_3': {
        'carol': LightningRpc('/wd/daemon-data/carol_chain_3/lightning-rpc'),
        'david': LightningRpc('/wd/daemon-data/david_chain_3/lightning-rpc'),
    },
    'chain_4': {
        'david': LightningRpc('/wd/daemon-data/david_chain_4/lightning-rpc'),
        'ezra': LightningRpc('/wd/daemon-data/ezra_chain_4/lightning-rpc'),
    },
    'chain_5': {
        'ezra': LightningRpc('/wd/daemon-data/ezra_chain_5/lightning-rpc'),
        'fiona': LightningRpc('/wd/daemon-data/fiona_chain_5/lightning-rpc'),
    },
}
LIGHTNINGD = select_chains(CHAINS, LIGHTNINGD)

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

# FIX the error in the handshake may be caused by the chain_hash being wrong in the hardcoded chainparams
ln_connect_nodes()

# TODO Create lightning channels

# TODO Pay from alice to fiona using lightning

print('All done. Exiting in 5 seconds...')
time.sleep(5)
