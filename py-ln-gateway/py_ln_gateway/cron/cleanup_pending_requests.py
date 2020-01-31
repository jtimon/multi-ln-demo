#!/usr/bin/env python3

if __name__ != '__main__':
    raise ImportError(u"%s may only be run as a script" % __file__)

from datetime import datetime
import time

from sqlalchemy import or_

from py_ln_gateway.db import db_session
from py_ln_gateway.models import (
    FailedRequest,
    PendingRequest,
)

count = 1
while True:
    print('total repetitions for %s = %s' % (__file__, count))
    utcnow = datetime.utcnow()
    pending_requests = PendingRequest.query.filter(or_(PendingRequest.src_expires_at < utcnow,
                                                       PendingRequest.dest_expires_at < utcnow))
    print('Expired pending requests =', pending_requests.count())
    for p in pending_requests:
        if p.src_expires_at < utcnow:
            error_msg = 'source invoice expired'
        else:
            error_msg = 'destination invoice expired'

        print('Expired pending request %s: %s' % (p.src_payment_hash, error_msg))
        db_session.add(FailedRequest(
            error = error_msg,
            src_payment_hash = p.src_payment_hash,
            src_chain = p.src_chain,
            src_bolt11 = p.src_bolt11,
            src_expires_at = p.src_expires_at,
            dest_chain = p.dest_chain,
            dest_bolt11 = p.dest_bolt11,
        ))
        db_session.delete(p)
        db_session.commit()

    count = count + 1
    time.sleep(30)
