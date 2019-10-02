
import time

# copied from https://github.com/cdecker/lightning-integration/blob/master/test.py
def wait_for(success, timeout=30, interval=1, label='something'):
    start_time = time.time()
    while not success() and time.time() < start_time + timeout:
        print('Waiting for %s (timeout=%d, interval=%d)' % (label, timeout, interval))
        time.sleep(interval)
    if time.time() > start_time + timeout:
        raise ValueError("Timeout error waiting for {}", success)
