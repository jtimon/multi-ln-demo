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

CHAINS = ['chain_1', 'chain_2', 'chain_3', 'chain_4', 'chain_5']
USERS = ['alice', 'bob', 'carol', 'david', 'ezra', 'fiona']

print('Chains considered:', CHAINS)
print('Users considered:', USERS)

BITCOIND = {
    'chain_1': {
        'alice': RpcCaller('0.0.0.0:18545', 'user18545', 'password18545'),
        'bob': RpcCaller('0.0.0.0:18645', 'user18645', 'password18645'),
    },
    'chain_2': {
        'bob': RpcCaller('0.0.0.0:18555', 'user18555', 'password18555'),
        'carol': RpcCaller('0.0.0.0:18655', 'user18655', 'password18655'),
    },
    # 'chain_3': {
    #     'carol': RpcCaller('0.0.0.0:18565', 'user18565', 'password18565'),
    #     'david': RpcCaller('0.0.0.0:18665', 'user18665', 'password18665'),
    # },
    # 'chain_4': {
    #     'david': RpcCaller('0.0.0.0:18575', 'user18575', 'password18575'),
    #     'ezra': RpcCaller('0.0.0.0:18675', 'user18675', 'password18675'),
    # },
    # 'chain_5': {
    #     'ezra': RpcCaller('0.0.0.0:18585', 'user18585', 'password18585'),
    #     'fiona': RpcCaller('0.0.0.0:18685', 'user18685', 'password18685'),
    # },
}

LIGHTNINGD = {
    'chain_1': {
        'alice': LightningRpc('/wd/daemon-data/alice_chain_1/lightning-rpc'),
        'bob': LightningRpc('/wd/daemon-data/bob_chain_1/lightning-rpc'),
    },
    'chain_2': {
        'bob': LightningRpc('/wd/daemon-data/bob_chain_2/lightning-rpc'),
        'carol': LightningRpc('/wd/daemon-data/carol_chain_2/lightning-rpc'),
    },
    # 'chain_3': {
    #     'carol': LightningRpc('/wd/daemon-data/carol_chain_3/lightning-rpc'),
    #     'david': LightningRpc('/wd/daemon-data/david_chain_3/lightning-rpc'),
    # },
    # 'chain_4': {
    #     'david': LightningRpc('/wd/daemon-data/david_chain_4/lightning-rpc'),
    #     'ezra': LightningRpc('/wd/daemon-data/ezra_chain_4/lightning-rpc'),
    # },
    # 'chain_5': {
    #     'ezra': LightningRpc('/wd/daemon-data/ezra_chain_5/lightning-rpc'),
    #     'fiona': LightningRpc('/wd/daemon-data/fiona_chain_5/lightning-rpc'),
    # },
}

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

# Wait for daemons to start
time.sleep(5)

# Connect all nodes of the same chain with each other
# TODO do this in a better way
connect_nodes(BITCOIND['chain_1']['alice'], '127.0.0.1:18646')
connect_nodes(BITCOIND['chain_1']['bob'], '127.0.0.1:18546')
connect_nodes(BITCOIND['chain_2']['bob'], '127.0.0.1:18656')
connect_nodes(BITCOIND['chain_2']['carol'], '127.0.0.1:18556')
# connect_nodes(BITCOIND['chain_3']['carol'], '127.0.0.1:18666')
# connect_nodes(BITCOIND['chain_3']['david'], '127.0.0.1:18566')
# connect_nodes(BITCOIND['chain_4']['david'], '127.0.0.1:18676')
# connect_nodes(BITCOIND['chain_4']['ezra'], '127.0.0.1:18576')
# connect_nodes(BITCOIND['chain_5']['ezra'], '127.0.0.1:18686')
# connect_nodes(BITCOIND['chain_5']['fiona'], '127.0.0.1:18586')

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

for chain_name, ln_daemons in LIGHTNINGD.items():
    for user_name, rpccaller in ln_daemons.items():
        print(chain_name, user_name, LIGHTNINGD[chain_name][user_name].getinfo())

for chain_name, ln_daemons in LIGHTNINGD.items():
    for user_name, rpccaller in ln_daemons.items():
        print(chain_name, user_name, LIGHTNINGD[chain_name][user_name].listfunds())

# TODO Create lightning channels

# TODO Pay from alice to fiona using lightning

print('All done. Exiting in 5 seconds...')
time.sleep(5)
