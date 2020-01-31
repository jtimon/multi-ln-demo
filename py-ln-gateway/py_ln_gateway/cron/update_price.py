#!/usr/bin/env python3

if __name__ != '__main__':
    raise ImportError(u"%s may only be run as a script" % __file__)

import json
import os
import time

from py_ln_gateway.db import db_session
from py_ln_gateway.models import Price

def add_or_update_price(src_chain, dest_chain, next_price_val):
    print('Updating price to %s for chain trade %s:%s' % (next_price_val, src_chain, dest_chain))
    price = Price.query.get('%s:%s' % (src_chain, dest_chain))
    if price:
        price.price = next_price_val
    else:
        db_session.add(Price(
            src_dest = '%s:%s' % (src_chain, dest_chain),
            price = next_price_val))
    db_session.commit()

# We really just need to set it once if it's going to be constant
with open(os.environ.get('PYGATEWAY_CONF')) as json_file:
    data = json.load(json_file)
    for d_price in data['default_prices']:
        add_or_update_price(d_price['src_chain'], d_price['dest_chain'], d_price['price'])

# This could periodically call the APIs of exchanges to update prices dynamically if necessary
# count = 1
# while True:
#     print('total repetitions for %s = %s' % (__file__, count))
#     count = count + 1
#     time.sleep(600)
