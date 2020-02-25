
from sqlalchemy import Column, DateTime, Integer, Numeric, String
from py_ln_gateway.db import Base

# There is no absolute limit for bolt11. There are practical limits based on QR code sizes.
# There's no maximum to find in the spec, but apparently 2048 for validation and storage is good enough as a guess.
# lnd accepts invoices up to 7089 bytes https://github.com/lightningnetwork/lnd/blob/master/zpay32/invoice.go#L79
MAX_BOLT11 = 2048
MAX_URL_LEN = 200

# TODO optimization: use bytes.fromhex() and store 32 bytes instead of 64 char hex string
# Find out best field for this on sqlalchemy
FIELD_32B_AS_HEX_STR = 64

class Price(Base):
    __tablename__ = 'prices'

    # The id is composed by the src_chain_id followed by ':' and then the dest_chain_id
    src_dest = Column(String((2 * FIELD_32B_AS_HEX_STR) + 1), primary_key=True)
    price = Column(Numeric(10,4), nullable=False)

class PendingRequest(Base):
    __tablename__ = 'pending_requests'

    src_payment_hash = Column(String(FIELD_32B_AS_HEX_STR), primary_key=True)

    src_chain = Column(String(FIELD_32B_AS_HEX_STR), nullable=False)
    src_bolt11 = Column(String(MAX_BOLT11), nullable=False)
    src_expires_at = Column(DateTime(), nullable=False)
    src_amount = Column(Integer(), nullable=False)

    dest_payment_hash = Column(String(FIELD_32B_AS_HEX_STR), nullable=False, unique=True)
    dest_chain = Column(String(64), nullable=False)
    dest_bolt11 = Column(String(MAX_BOLT11), nullable=False)
    dest_expires_at = Column(DateTime(), nullable=False)
    dest_amount = Column(Integer(), nullable=False)

    other_gw_payment_hash = Column(String(FIELD_32B_AS_HEX_STR))
    other_gw_url = Column(String(MAX_URL_LEN))
    other_gw_chain = Column(String(64))
    other_gw_bolt11 = Column(String(MAX_BOLT11))
    other_gw_expires_at = Column(DateTime())
    other_gw_amount = Column(Integer())

class PaidRequest(Base):
    __tablename__ = 'paid_requests'

    src_payment_hash = Column(String(FIELD_32B_AS_HEX_STR), primary_key=True)

    src_chain = Column(String(FIELD_32B_AS_HEX_STR), nullable=False)
    src_bolt11 = Column(String(MAX_BOLT11), nullable=False)
    src_expires_at = Column(DateTime(), nullable=False)
    src_payment_preimage = Column(String(FIELD_32B_AS_HEX_STR), nullable=False)

    dest_payment_hash = Column(String(FIELD_32B_AS_HEX_STR), nullable=False, unique=True)
    dest_chain = Column(String(FIELD_32B_AS_HEX_STR), nullable=False)
    dest_bolt11 = Column(String(MAX_BOLT11), nullable=False)
    dest_expires_at = Column(DateTime(), nullable=False)
    dest_payment_preimage = Column(String(FIELD_32B_AS_HEX_STR), nullable=False)

    other_gw_payment_hash = Column(String(FIELD_32B_AS_HEX_STR))
    other_gw_url = Column(String(MAX_URL_LEN))
    other_gw_chain = Column(String(FIELD_32B_AS_HEX_STR))
    other_gw_bolt11 = Column(String(MAX_BOLT11))
    other_gw_expires_at = Column(DateTime())
    other_gw_payment_preimage = Column(String(FIELD_32B_AS_HEX_STR))

class FailedRequest(Base):
    __tablename__ = 'failed_requests'

    src_payment_hash = Column(String(FIELD_32B_AS_HEX_STR), primary_key=True)

    error = Column(String(2500))
    src_payment_preimage = Column(String(FIELD_32B_AS_HEX_STR))

    src_chain = Column(String(FIELD_32B_AS_HEX_STR), nullable=False)
    src_bolt11 = Column(String(MAX_BOLT11), nullable=False)
    src_expires_at = Column(DateTime(), nullable=False)
    src_amount = Column(Integer(), nullable=False)

    dest_payment_hash = Column(String(FIELD_32B_AS_HEX_STR), nullable=False, unique=True)
    dest_chain = Column(String(FIELD_32B_AS_HEX_STR), nullable=False)
    dest_bolt11 = Column(String(MAX_BOLT11), nullable=False)
    dest_expires_at = Column(DateTime(), nullable=False)
    dest_amount = Column(Integer(), nullable=False)

    other_gw_payment_hash = Column(String(FIELD_32B_AS_HEX_STR))
    other_gw_url = Column(String(MAX_URL_LEN))
    other_gw_chain = Column(String(64))
    other_gw_bolt11 = Column(String(MAX_BOLT11))
    other_gw_expires_at = Column(DateTime())
    other_gw_amount = Column(Integer())
    other_gw_payment_preimage = Column(String(FIELD_32B_AS_HEX_STR))
