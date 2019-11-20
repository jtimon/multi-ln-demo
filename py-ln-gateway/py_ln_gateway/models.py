from py_ln_gateway import db

class Price(db.Model):
    __tablename__ = 'prices'

    id = db.Column(db.Integer, primary_key=True)

    # FIX optimization: binascii.unhexlify and store 32 bytes instead of 64 char hex string
    # FIX make src_chain and dest_chain unique together and the id, and have a getter
    src_chain = db.Column(db.String(64))
    dest_chain = db.Column(db.String(64))
    price = db.Column(db.Numeric(10,4))

# FIX DoS: Don't store pending request forever (cron job to remove old ones)
# FIX DoS: explicitly configure the max disk to be used on pending requests (or at least the number of entries)
class PendingRequest(db.Model):
    __tablename__ = 'pending_requests'

    # FIX optimization: binascii.unhexlify and store 32 bytes instead of 64 char hex string
    src_payment_hash = db.Column(db.String(64), primary_key=True)

    # FIX optimization: binascii.unhexlify and store 32 bytes instead of 64 char hex string
    src_chain = db.Column(db.String(64))
    # TODO this could be simply a getter using Gateway.chains_by_bip173
    src_chain_petname = db.Column(db.String(256))
    # TODO check the actual limit for bolt11
    src_bolt11 = db.Column(db.String(2048))
    # TODO turn into datetime field
    src_expires_at = db.Column(db.String(256))

    dest_chain = db.Column(db.String(64))
    dest_chain_petname = db.Column(db.String(256))
    dest_bolt11 = db.Column(db.String(2048))
    # TODO add dest_expires_at

class PaidRequest(db.Model):
    __tablename__ = 'paid_requests'

    # FIX optimization: binascii.unhexlify and store 32 bytes instead of 64 char hex string
    src_payment_hash = db.Column(db.String(64), primary_key=True)

    # FIX optimization: binascii.unhexlify and store 32 bytes instead of 64 char hex string
    src_chain = db.Column(db.String(64))
    # TODO this could be simply a getter using Gateway.chains_by_bip173
    src_chain_petname = db.Column(db.String(256))
    # TODO check the actual limit for bolt11
    src_bolt11 = db.Column(db.String(2048))
    # TODO turn into datetime field
    src_expires_at = db.Column(db.String(256))
    # FIX optimization: binascii.unhexlify and store 32 bytes instead of 64 char hex string
    src_payment_preimage = db.Column(db.String(64)),

    dest_payment_hash = db.Column(db.String(64)),
    dest_chain = db.Column(db.String(64))
    dest_chain_petname = db.Column(db.String(256))
    dest_bolt11 = db.Column(db.String(2048))
    # TODO add dest_expires_at
    dest_payment_preimage = db.Column(db.String(64)),

class FailedRequest(db.Model):
    __tablename__ = 'failed_requests'

    # FIX optimization: binascii.unhexlify and store 32 bytes instead of 64 char hex string
    src_payment_hash = db.Column(db.String(64), primary_key=True)

    # FIX optimization: binascii.unhexlify and store 32 bytes instead of 64 char hex string
    src_chain = db.Column(db.String(64))
    # TODO this could be simply a getter using Gateway.chains_by_bip173
    src_chain_petname = db.Column(db.String(256))
    # TODO check the actual limit for bolt11
    src_bolt11 = db.Column(db.String(2048))
    # TODO turn into datetime field
    src_expires_at = db.Column(db.String(256))
    # FIX optimization: binascii.unhexlify and store 32 bytes instead of 64 char hex string
    src_payment_preimage = db.Column(db.String(64)),

    dest_chain = db.Column(db.String(64))
    dest_chain_petname = db.Column(db.String(256))
    dest_bolt11 = db.Column(db.String(2048))
    # TODO add dest_expires_at
