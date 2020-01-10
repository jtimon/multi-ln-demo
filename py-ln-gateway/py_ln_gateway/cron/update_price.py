#!/usr/bin/env python3

if __name__ != '__main__':
    raise ImportError(u"%s may only be run as a script" % __file__)

import time

from py_ln_gateway.app import app
from py_ln_gateway.db import db_session
from py_ln_gateway.models import Price

app.app_context().push()

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
add_or_update_price('0f9188f13cb7b2c71f2a335e3a4fc328bf5beb436012afca590b1a11466e2206',
                    '9f87eb580b9e5f11dc211e9fb66abb3699999044f8fe146801162393364286c6',
                    1)

count = 1
while True:
    print('total repetitions for %s = %s' % (__file__, count))
    # This could periodically call the API for exchanges to update prices
    add_or_update_price('0f9188f13cb7b2c71f2a335e3a4fc328bf5beb436012afca590b1a11466e2206',
                        '9f87eb580b9e5f11dc211e9fb66abb3699999044f8fe146801162393364286c6',
                        1)
    count = count + 1
    time.sleep(60)
