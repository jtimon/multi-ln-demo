
from pprint import pprint
import time

from multiln.rpccaller import RpcCaller

def btc_init_bitcoind_global(chains):
    to_return = {}
    for chain_name in chains:
        port_chain = '185%s5' % (chains[chain_name]['port_decimal'])
        to_return[chain_name] = RpcCaller(
            '%s:%s' % (chains[chain_name]['host_url'], port_chain),
            'user%s' % port_chain,
            'password%s' % port_chain,
        )
    return to_return

def btc_wait_deamons_start(bitcoind_map):
    for chain_name, rpccaller in bitcoind_map.items():
        while True:
            print('Waiting bitcoind for chain %s to start' % chain_name)
            if not 'error' in rpccaller.call('help', {}):
                break
            time.sleep(1)


def generate_blocks(rpccaller, chain_name, nblocks):
    address = rpccaller.call('getnewaddress', {})
    block_hashes = rpccaller.call('generatetoaddress', {'nblocks': nblocks, 'address': address})
    print('Generated %s %s blocks:' % (nblocks, chain_name))
    # print(block_hashes)

def btc_generate_all_chains(bitcoind_map, nblocks):
    for chain_name, rpccaller in bitcoind_map.items():
        generate_blocks(rpccaller, chain_name, nblocks)

def print_balances(bitcoind_map):
    for chain_name, rpccaller in bitcoind_map.items():
        print('getbalance', chain_name, rpccaller.call('getbalance', {}))
        print('getbalances', chain_name, rpccaller.call('getbalances', {}))

def btc_print_block_at_height(bitcoind_map, height):
    for chain_name, rpccaller in bitcoind_map.items():
        blockhash = rpccaller.call('getblockhash', {'height': height})
        print('getblockhash', chain_name, blockhash)
        block = rpccaller.call('getblock', {'blockhash': blockhash})
        for txid in block['tx']:
            tx = rpccaller.call('getrawtransaction', {'blockhash': blockhash, 'txid': txid, 'verbose': 1})
            print('getrawtransaction', chain_name)
            pprint(tx)
