from py_ln_gateway.db import db

# There is no absolute limit for bolt11. There are practical limits based on QR code sizes.
# There's no maximum to find in the spec, but apparently 2048 for validation and storage is good enough as a guess.
# lnd accepts invoices up to 7089 bytes https://github.com/lightningnetwork/lnd/blob/master/zpay32/invoice.go#L79
MAX_BOLT11 = 2048

# TODO optimization: binascii.unhexlify and store 32 bytes instead of 64 char hex string
# Find out best field for this on sqlalchemy
FIELD_32B_AS_HEX_STR = 64

class Price(db.Model):
    __tablename__ = 'prices'

    # The id is composed by the src_chain_id followed by ':' and then the dest_chain_id
    src_dest = db.Column(db.String((2 * FIELD_32B_AS_HEX_STR) + 1), primary_key=True)
    # TODO FIX Warning: Dialect sqlite+pysqlite does *not* support Decimal objects natively, and SQLAlchemy must convert from floating point - rounding errors and other issues may occur. Please consider storing Decimal numbers as strings or integers on this platform for lossless storage.
    price = db.Column(db.Numeric(10,4))

class PendingRequest(db.Model):
    __tablename__ = 'pending_requests'

    src_payment_hash = db.Column(db.String(FIELD_32B_AS_HEX_STR), primary_key=True)

    src_chain = db.Column(db.String(FIELD_32B_AS_HEX_STR))
    src_bolt11 = db.Column(db.String(MAX_BOLT11))
    src_expires_at = db.Column(db.DateTime())
    src_amount = db.Column(db.Integer())

    dest_chain = db.Column(db.String(64))
    dest_bolt11 = db.Column(db.String(MAX_BOLT11))
    dest_expires_at = db.Column(db.DateTime())
    dest_amount = db.Column(db.Integer())

class PaidRequest(db.Model):
    __tablename__ = 'paid_requests'

    src_payment_hash = db.Column(db.String(FIELD_32B_AS_HEX_STR), primary_key=True)

    src_chain = db.Column(db.String(FIELD_32B_AS_HEX_STR))
    src_bolt11 = db.Column(db.String(MAX_BOLT11))
    src_expires_at = db.Column(db.DateTime())
    src_payment_preimage = db.Column(db.String(FIELD_32B_AS_HEX_STR))

    dest_payment_hash = db.Column(db.String(FIELD_32B_AS_HEX_STR))
    dest_chain = db.Column(db.String(FIELD_32B_AS_HEX_STR))
    dest_bolt11 = db.Column(db.String(MAX_BOLT11))
    dest_expires_at = db.Column(db.DateTime())
    dest_payment_preimage = db.Column(db.String(FIELD_32B_AS_HEX_STR))

class FailedRequest(db.Model):
    __tablename__ = 'failed_requests'

    error = db.Column(db.String(2500))
    src_payment_hash = db.Column(db.String(FIELD_32B_AS_HEX_STR), primary_key=True)

    src_chain = db.Column(db.String(FIELD_32B_AS_HEX_STR))
    src_bolt11 = db.Column(db.String(MAX_BOLT11))
    src_expires_at = db.Column(db.DateTime())
    src_payment_preimage = db.Column(db.String(FIELD_32B_AS_HEX_STR), nullable=True)

    dest_chain = db.Column(db.String(FIELD_32B_AS_HEX_STR))
    dest_bolt11 = db.Column(db.String(MAX_BOLT11))
    dest_expires_at = db.Column(db.DateTime())
