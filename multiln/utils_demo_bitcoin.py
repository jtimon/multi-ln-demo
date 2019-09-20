
from multiln.bitcoin_test_utils import (
    connect_nodes,
    sync_blocks,
)
from multiln.rpccaller import RpcCaller

def get_p2p_decimal_1(chains, chain_name, user_name):
    # TODO This only scales to 2 nodes per chain
    if chains[chain_name]['main_user'] == user_name:
        return '5'
    else:
        return '6'

def get_p2p_port(chains, chain_name, user_name):
    return '18%s%s6' % (
        # TODO This only scales to 2 nodes per chain
        get_p2p_decimal_1(chains, chain_name, user_name),
        chains[chain_name]['port_decimal'],
    )

def btc_init_bitcoind_global(chains):
    to_return = {}
    for chain_name in chains:
        to_return[chain_name] = {}
        for user_name in chains[chain_name]['users']:
            port_chain_user = '18%s%s5' % (
                get_p2p_decimal_1(chains, chain_name, user_name),
                chains[chain_name]['port_decimal'],
            )
            to_return[chain_name][user_name] = RpcCaller(
                '0.0.0.0:%s' % port_chain_user,
                'user%s' % port_chain_user,
                'password%s' % port_chain_user,
            )
    return to_return


'''Connect all nodes of the same chain with each other'''
def btc_connect_nodes(chains, bitcoind_map):
    for chain_name, chain_daemons in bitcoind_map.items():
        for user_name_a, rpccaller in chain_daemons.items():
            for user_name_b in chain_daemons:
                if user_name_a != user_name_b:
                    connect_nodes(bitcoind_map[chain_name][user_name_a], '127.0.0.1:%s' % get_p2p_port(chains, chain_name, user_name_b))

def generate_blocks(bitcoind_map, rpccaller, chain_name, nblocks):
    address = rpccaller.call('getnewaddress', {})
    block_hashes = rpccaller.call('generatetoaddress', {'nblocks': nblocks, 'address': address})
    print('Generated %s %s blocks:' % (nblocks, chain_name))
    # print(block_hashes)
    sync_blocks(bitcoind_map[chain_name].values())

def btc_generate_all_chains(bitcoind_map, nblocks):
    for chain_name, chain_daemons in bitcoind_map.items():
        # Any daemon for each chain will do
        rpccaller = next(iter(chain_daemons.values()))
        generate_blocks(bitcoind_map, rpccaller, chain_name, nblocks)

def print_balances(bitcoind_map):
    for chain_name, chain_daemons in bitcoind_map.items():
        for user_name, rpccaller in chain_daemons.items():
            print(chain_name, user_name, rpccaller.call('getbalances', {}))
