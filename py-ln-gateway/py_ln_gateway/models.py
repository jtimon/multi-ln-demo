from py_ln_gateway import db

# There is no absolute limit for bolt11. There are practical limits based on QR code sizes.
# There's no maximum to find in the spec, but apparently 2048 for validation and storage is good enough as a guess.
# lnd accepts invoices up to 7089 bytes https://github.com/lightningnetwork/lnd/blob/master/zpay32/invoice.go#L79
MAX_BOLT11 = 2048

# TODO optimization: binascii.unhexlify and store 32 bytes instead of 64 char hex string
# Find out best field for this on sqlalchemy
FIELD_32B_AS_HEX_STR = 64

class Price(db.Model):
    __tablename__ = 'prices'

    id = db.Column(db.Integer, primary_key=True)

    # TODO make src_chain and dest_chain unique together and the id, and have a getter
    src_chain = db.Column(db.String(FIELD_32B_AS_HEX_STR))
    dest_chain = db.Column(db.String(FIELD_32B_AS_HEX_STR))
    # TODO FIX Warning: Dialect sqlite+pysqlite does *not* support Decimal objects natively, and SQLAlchemy must convert from floating point - rounding errors and other issues may occur. Please consider storing Decimal numbers as strings or integers on this platform for lossless storage.
    price = db.Column(db.Numeric(10,4))

# TODO FIX DoS: Don't store pending request forever (cron job to remove old ones)
# Perhaps just explicitly configure the max disk to be used on pending requests (or at least the number of entries)
class PendingRequest(db.Model):
    __tablename__ = 'pending_requests'

    src_payment_hash = db.Column(db.String(FIELD_32B_AS_HEX_STR), primary_key=True)

    src_chain = db.Column(db.String(FIELD_32B_AS_HEX_STR))
    src_bolt11 = db.Column(db.String(MAX_BOLT11))
    # TODO optimization: turn _expires_at fields into datetime fields
    src_expires_at = db.Column(db.String(256))
    # TODO add dest_expires_at fields in PendingRequest, PaidRequest and FailedRequest, why not?

    dest_chain = db.Column(db.String(64))
    dest_bolt11 = db.Column(db.String(MAX_BOLT11))

class PaidRequest(db.Model):
    __tablename__ = 'paid_requests'

    src_payment_hash = db.Column(db.String(FIELD_32B_AS_HEX_STR), primary_key=True)

    src_chain = db.Column(db.String(FIELD_32B_AS_HEX_STR))
    src_bolt11 = db.Column(db.String(MAX_BOLT11))
    src_expires_at = db.Column(db.String(256))
    src_payment_preimage = db.Column(db.String(FIELD_32B_AS_HEX_STR)),

    dest_payment_hash = db.Column(db.String(FIELD_32B_AS_HEX_STR)),
    dest_chain = db.Column(db.String(FIELD_32B_AS_HEX_STR))
    dest_bolt11 = db.Column(db.String(MAX_BOLT11))
    dest_payment_preimage = db.Column(db.String(FIELD_32B_AS_HEX_STR)),

class FailedRequest(db.Model):
    __tablename__ = 'failed_requests'

    src_payment_hash = db.Column(db.String(FIELD_32B_AS_HEX_STR), primary_key=True)

    src_chain = db.Column(db.String(FIELD_32B_AS_HEX_STR))
    src_bolt11 = db.Column(db.String(MAX_BOLT11))
    src_expires_at = db.Column(db.String(256))
    src_payment_preimage = db.Column(db.String(FIELD_32B_AS_HEX_STR)),

    dest_chain = db.Column(db.String(FIELD_32B_AS_HEX_STR))
    dest_bolt11 = db.Column(db.String(MAX_BOLT11))
