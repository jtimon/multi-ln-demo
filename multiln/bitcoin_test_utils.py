# Code copied from Bitcoin Core project and slightly modified to fit our needs

import time

def wait_until(predicate, *, attempts=float('inf'), timeout=float('inf'), lock=None):
    if attempts == float('inf') and timeout == float('inf'):
        timeout = 60
    attempt = 0
    time_end = time.time() + timeout

    while attempt < attempts and time.time() < time_end:
        if lock:
            with lock:
                if predicate():
                    return
        else:
            if predicate():
                return
        attempt += 1
        time.sleep(0.05)

    # Print the cause of the timeout
    predicate_source = "''''\n" + inspect.getsource(predicate) + "'''"
    if attempt >= attempts:
        raise AssertionError("Predicate {} not true after {} attempts".format(predicate_source, attempts))
    elif time.time() >= time_end:
        raise AssertionError("Predicate {} not true after {} seconds".format(predicate_source, timeout))
    raise RuntimeError('Unreachable')

def connect_nodes(rpccaller, ip_port):
    rpccaller.call('addnode', {'node': ip_port, 'command': 'onetry'})
    # poll until version handshake complete to avoid race conditions
    # with transaction relaying
    wait_until(lambda:  all(peer['version'] != 0 for peer in rpccaller.call('getpeerinfo', {})))

def connect_nodes_bi(node_a, node_b, ip_a, ip_b):
    connect_nodes(node_a, ip_b)
    connect_nodes(node_b, node_a, ip_b)

def sync_blocks(rpccallers, wait=1, timeout=60):
    """
    Wait until everybody has the same tip.

    sync_blocks needs to be called with an rpc_connections set that has least
    one node already synced to the latest, stable tip, otherwise there's a
    chance it might return before all nodes are stably synced.
    """
    stop_time = time.time() + timeout
    while time.time() <= stop_time:
        best_hash = [x.call('getbestblockhash', {}) for x in rpccallers]
        if best_hash.count(best_hash[0]) == len(rpccallers):
            return
        time.sleep(wait)
    raise AssertionError("Block sync timed out:{}".format("".join("\n  {!r}".format(b) for b in best_hash)))
