from py_ln_gateway import db

# There is no absolute limit for bolt11. There are practical limits based on QR code sizes.
# There's no maximum to find in the spec, but apparently 2048 for validation and storage is good enough as a guess.
MAX_BOLT11 = 2048

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
    src_bolt11 = db.Column(db.String(MAX_BOLT11))
    # TODO turn into datetime field
    src_expires_at = db.Column(db.String(256))

    dest_chain = db.Column(db.String(64))
    dest_bolt11 = db.Column(db.String(MAX_BOLT11))
    # TODO add dest_expires_at

class PaidRequest(db.Model):
    __tablename__ = 'paid_requests'

    # FIX optimization: binascii.unhexlify and store 32 bytes instead of 64 char hex string
    src_payment_hash = db.Column(db.String(64), primary_key=True)

    # FIX optimization: binascii.unhexlify and store 32 bytes instead of 64 char hex string
    src_chain = db.Column(db.String(64))
    src_bolt11 = db.Column(db.String(MAX_BOLT11))
    # TODO turn into datetime field
    src_expires_at = db.Column(db.String(256))
    # FIX optimization: binascii.unhexlify and store 32 bytes instead of 64 char hex string
    src_payment_preimage = db.Column(db.String(64)),

    dest_payment_hash = db.Column(db.String(64)),
    dest_chain = db.Column(db.String(64))
    dest_bolt11 = db.Column(db.String(MAX_BOLT11))
    # TODO add dest_expires_at
    dest_payment_preimage = db.Column(db.String(64)),

class FailedRequest(db.Model):
    __tablename__ = 'failed_requests'

    # FIX optimization: binascii.unhexlify and store 32 bytes instead of 64 char hex string
    src_payment_hash = db.Column(db.String(64), primary_key=True)

    # FIX optimization: binascii.unhexlify and store 32 bytes instead of 64 char hex string
    src_chain = db.Column(db.String(64))
    src_bolt11 = db.Column(db.String(MAX_BOLT11))
    # TODO turn into datetime field
    src_expires_at = db.Column(db.String(256))
    # FIX optimization: binascii.unhexlify and store 32 bytes instead of 64 char hex string
    src_payment_preimage = db.Column(db.String(64)),

    dest_chain = db.Column(db.String(64))
    dest_bolt11 = db.Column(db.String(MAX_BOLT11))
    # TODO add dest_expires_at
