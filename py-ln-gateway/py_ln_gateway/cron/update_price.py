#!/usr/bin/env python3

if __name__ != '__main__':
    raise ImportError(u"%s may only be run as a script" % __file__)

import time

from py_ln_gateway.app import app
from py_ln_gateway.db import db
from py_ln_gateway.models import Price

app.app_context().push()

# We just need to set it once if it's going to be constant
db.session.add(Price(
    src_chain = '58ebd25d25b128530d4d462c65a7e679b7e053e6f25ffb8ac63bc68832fda201',
    dest_chain = 'e07d79a4f8f1525814e421eb71aa9527fe8a25091fe1b9c5c312939c887aadc7',
    price = 1))
db.session.commit()

count = 1
while True:
    print('total repetitions for %s = %s' % (__file__, count))
    # This could periodically call the API for exchanges to update prices
    count = count + 1
    time.sleep(60)
