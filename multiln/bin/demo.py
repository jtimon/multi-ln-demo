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
    'regtest': {
        'port_decimal': 1
    },
    # 'chain_1': {
    #     'port_decimal': 4
    # },
    # 'chain_2': {
    #     'port_decimal': 5
    # },
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
    'regtest': ['alice', 'bob'],
    'chain_1': ['alice', 'bob'],
    'chain_2': ['bob', 'carol'],
    'chain_3': ['carol', 'david'],
    'chain_4': ['david', 'ezra'],
    'chain_5': ['ezra', 'fiona'],
}

MAIN_USER_PER_CHAIN = {
    'regtest': 'alice',
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
                    print('Connecting %s to %s in chain %s, port %s' % (
                        user_name_a, user_name_b, chain_name, info_b['binding'][0]['port']))
                    rpccaller.connect(info_b['id'], host='0.0.0.0', port=info_b['binding'][0]['port'])

# TODO find a smarter and faster way to sync lightning nodes with their respective bitcoind
def ln_btc_sync():
    time.sleep(30)
    # for chain_name, chain_daemons in BITCOIND.items():
    #     for user_name, rpccaller in chain_daemons.items():
    #         print(LIGHTNINGD[chain_name][user_name].dev_rescan_outputs())

##################################

# Wait for daemons to start
time.sleep(5)

btc_connect_nodes()
ln_update_info()
ln_connect_nodes()

# Let's make sure everyone generates some coins in the chains they participate in
for chain_name, chain_daemons in BITCOIND.items():
    for rpccaller in chain_daemons.values():
        generate_blocks(rpccaller, chain_name, 1)

# Let's mature the coins in each chain
btc_generate_all_chains(100)

print_balances()

# Alice can pay bob directly on regtest
bob_address = BITCOIND['regtest']['bob'].call('getnewaddress', {})
txid = BITCOIND['regtest']['alice'].call('sendtoaddress', {'address': bob_address, 'amount': 1})
print('Alice can pay bob directly on regtest (txid: %s)' % txid)
generate_blocks(BITCOIND['regtest']['alice'], 'regtest', 1)
print_balances()

# Send coins to all lightning wallets
for chain_name, chain_daemons in BITCOIND.items():
    for user_name, rpccaller in chain_daemons.items():
        print(rpccaller.call('getbalances', {}))
        address = LIGHTNINGD[chain_name][user_name].newaddr('p2sh-segwit')['p2sh-segwit']
        txid = rpccaller.call('sendtoaddress', {'address': address, 'amount': 10})
        print('%s %s: sending coins to address %s in lightning wallet (txid: %s)' % (chain_name, user_name, address, txid))
        generate_blocks(rpccaller, chain_name, 1)

# Wait for lightningd to sync with bitcoind
ln_btc_sync()

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
ln_btc_sync()
ln_assert_channels_state('CHANNELD_NORMAL')
ln_assert_channels_public(False)

ln_listchannels()
# After 6 confirmations it becomes public
btc_generate_all_chains(5)
ln_btc_sync()
ln_listchannels()
ln_assert_channels_public(True)

# TODO Create lightning channels

# TODO Pay from alice to fiona using lightning

# import json
# print(json.dumps(LIGHTNINGD['regtest']['alice'].help(), indent=4, sort_keys=True))

print('All done. Exiting in 5 seconds...')
time.sleep(5)
