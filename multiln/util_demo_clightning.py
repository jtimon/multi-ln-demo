
import time

from lightning import LightningRpc

def ln_init_global(chains):
    to_return = {}
    for chain_name in chains:
        to_return[chain_name] = {}
        for user_name in chains[chain_name]['users']:
            to_return[chain_name][user_name] = LightningRpc('/wd/daemon-data/%s_%s/lightning-rpc' % (user_name, chain_name))
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
                except TypeError as e:
                    print('TypeError:', e)
                except FileNotFoundError as e:
                    print('FileNotFoundError:', e)
                time.sleep(1)

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
                    rpccaller.connect(info_b['id'], host='0.0.0.0', port=info_b['binding'][0]['port'])

# wait for everyone to have some onchain funds on every chain they're in
def ln_wait_initial_funds(lightningd_map):
    for chain_name, chain_daemons in lightningd_map.items():
        for user_name, rpccaller in chain_daemons.items():
            while True:
                try:
                    if len(lightningd_map[chain_name][user_name].listfunds()['outputs']) > 0:
                        break
                except TypeError as e:
                    print('TypeError:', e)
                except ValueError as e:
                    print('ValueError:', e)
                print('Waiting for user %s initial funds on chain %s (lightning node)' % (user_name, chain_name))
                time.sleep(1)
