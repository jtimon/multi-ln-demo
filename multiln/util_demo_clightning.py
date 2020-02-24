
import time

from pyln.client import LightningRpc

from multiln.util import wait_for

def ln_init_global(chains):
    to_return = {}
    for chain_name in chains:
        to_return[chain_name] = {}
        for user_name in chains[chain_name]['users']:
            to_return[chain_name][user_name] = LightningRpc('/wd/clightning_datadir_%s/%s/lightning-rpc' % (
                user_name, chain_name))
    return to_return

def ln_wait_deamons_start(lightningd_map):
    for chain_name, ln_daemons in lightningd_map.items():
        for user_name, ln_caller in ln_daemons.items():
            while True:
                print('Waiting lightningd for user %s in chain %s to start' % (user_name, chain_name))
                try:
                    info = ln_caller.getinfo()
                    if isinstance(info, dict):
                        break
                except ValueError as e:
                    print('ValueError:', e)
                except ConnectionRefusedError as e:
                    print('ConnectionRefusedError:', e)
                except TypeError as e:
                    print('TypeError:', e)
                except FileNotFoundError as e:
                    print('FileNotFoundError:', e)
                time.sleep(1)

# copied from https://github.com/cdecker/lightning-integration/blob/master/test.py (modified)
def sync_blockheight(rpccaller, nodes, timeout=30, interval=1, label='sync_blockheight'):
    info = rpccaller.call('getblockchaininfo', {})
    blocks = info['blocks']

    label = "%s to block height %d" % (label, blocks)
    for n in nodes:
        wait_for(lambda: n.getinfo()['blockheight'] == blocks, timeout=timeout, interval=interval, label=label)

def ln_sync_blockheight(bitcoind_map, lightningd_map, timeout=30, interval=1, label='ln_sync_blockheight'):
    for chain_name, ln_daemons in lightningd_map.items():
        ln_nodes = []
        for user_name, ln_caller in ln_daemons.items():
            ln_nodes.append(ln_caller)
        label = "%s: %d nodes in chain %s to sync" % (label, len(ln_nodes), chain_name)
        sync_blockheight(bitcoind_map[chain_name], ln_nodes, timeout=timeout, interval=interval, label=label)


def ln_init_info(lightningd_map):
    ln_info = {}
    for chain_name, ln_daemons in lightningd_map.items():
        ln_info[chain_name] = {}
        for user_name, ln_caller in ln_daemons.items():
            ln_info[chain_name][user_name] = ln_caller.getinfo()
    return ln_info

def ln_print_info(ln_info):
    for chain_name, ln_users in ln_info.items():
        for user_name, info in ln_users.items():
            print(chain_name, user_name, info)

def ln_listfunds(lightningd_map):
    for chain_name, ln_daemons in lightningd_map.items():
        for user_name, ln_caller in ln_daemons.items():
            print(chain_name, user_name, ln_caller.listfunds())

def ln_listchannels(lightningd_map):
    for chain_name, ln_daemons in lightningd_map.items():
        for user_name, ln_caller in ln_daemons.items():
            print(chain_name, user_name, ln_caller.listchannels())

def ln_listpeers(lightningd_map):
    for chain_name, ln_daemons in lightningd_map.items():
        for user_name, ln_caller in ln_daemons.items():
            print(chain_name, user_name, ln_caller.listpeers())

def ln_assert_channels_state(lightningd_map, state):
    for chain_name, ln_daemons in lightningd_map.items():
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

def ln_wait_channels_state(lightningd_map, state, wait_interval=5):
    ready = False
    while not ready:
        ready = True
        for chain_name, ln_daemons in lightningd_map.items():
            for user_name, ln_caller in ln_daemons.items():
                for peer in ln_caller.listpeers()['peers']:
                    for channel in peer['channels']:
                        if state != channel['state']:
                            ready = False
                            print('Waiting channel for user %s in chain %s to get to state %s (currently in %s)' % (
                                user_name, chain_name, state, channel['state']))
                            break
        time.sleep(wait_interval)

def ln_assert_channels_public(lightningd_map, expected_public):
    for chain_name, ln_daemons in lightningd_map.items():
        for user_name, ln_caller in ln_daemons.items():
            for channel in ln_caller.listchannels()['channels']:
                if expected_public != channel['public']:
                    raise AssertionError('%s %s: Expected channel.public to be %s, but it was not' % (
                        chain_name,
                        user_name,
                        expected_public,
                    ))


# Connect all lightning nodes in the same chain to each other
def ln_connect_nodes(lightningd_map, ln_info):
    for chain_name, ln_daemons in lightningd_map.items():
        for user_name_a, rpccaller in lightningd_map[chain_name].items():
            for user_name_b, info_b in ln_info[chain_name].items():
                if user_name_a != user_name_b:
                    print('Connecting %s to %s in chain %s, port %s id %s' % (
                        user_name_a, user_name_b, chain_name, info_b['binding'][0]['port'], info_b['id']))
                    rpccaller.connect(info_b['id'],
                                      host='clightning_%s_%s' % (user_name_b, chain_name.replace("-", "_")),
                                      port=info_b['binding'][0]['port'])
