#!/usr/bin/env python3

if __name__ != '__main__':
    raise ImportError(u"%s may only be run as a script" % __file__)

import time
from multiln.rpccaller import RpcCaller

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

# Wait for daemons to start
time.sleep(5)

def generate_blocks(rpccaller, chain_name, nblocks):
    address = rpccaller.call('getnewaddress', {})
    print('Generated address %s' % address)
    block_hashes = rpccaller.call('generatetoaddress', {'nblocks': nblocks, 'address': address})
    print('Generated %s blocks:' % chain_name)
    print(block_hashes)

# Let's make sure everyone generates some coins in the chains they participate in
for chain_name, chain_daemons in BITCOIND.items():
    for rpccaller in chain_daemons.values():
        generate_blocks(rpccaller, chain_name, 1)

# Let's mature the coins in each chain
for chain_daemons in BITCOIND.values():
    # Any daemon for each chain will do
    rpccaller = next(iter(chain_daemons.values()))
    generate_blocks(rpccaller, chain_name, 101)


# Alice can pay bob directly on chain_1
bob_address = BITCOIND['chain_1']['bob'].call('getnewaddress', {})
txid = BITCOIND['chain_1']['alice'].call('sendtoaddress', {'address': bob_address, 'amount': 1})
print('Alice can pay bob directly on chain_1 (txid: %s)' % txid)
generate_blocks(BITCOIND['chain_1']['alice'], 'chain_1', 1)


# TODO Create lightning channels

# TODO Pay from alice to fiona using lightning

print('All done. Exiting in 5 seconds...')
time.sleep(5)
