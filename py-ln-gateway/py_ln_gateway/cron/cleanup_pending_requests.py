#!/usr/bin/env python3

if __name__ != '__main__':
    raise ImportError(u"%s may only be run as a script" % __file__)

from datetime import datetime
import time

from sqlalchemy import or_

from py_ln_gateway.db import db_session
from py_ln_gateway.models import (
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
        db_session.delete(p)
        db_session.commit()
        # TODO call lightning-cli delinvoice for the src_invoice
        # is there a way to remove all expired invoices at once better than listinvoices, filter by status=expired, then iteratively call delinvoice?

    count = count + 1
    time.sleep(30)
