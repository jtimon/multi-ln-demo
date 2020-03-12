
from sqlalchemy import Column, DateTime, Integer, Numeric, String, LargeBinary, TypeDecorator
from py_ln_gateway.db import Base

# There is no absolute limit for bolt11. There are practical limits based on QR code sizes.
# There's no maximum to find in the spec, but apparently 2048 for validation and storage is good enough as a guess.
# lnd accepts invoices up to 7089 bytes https://github.com/lightningnetwork/lnd/blob/master/zpay32/invoice.go#L79
MAX_BOLT11 = 2048
MAX_URL_LEN = 200

class ByteHexString(TypeDecorator):
    """Convert a string with hexadecimal digits to bytestring for storage and back."""
    impl = LargeBinary

    def process_bind_param(self, value, dialect):
        if not value:
            return None
        if not isinstance(value, str):
            raise TypeError("ByteHexString columns support only str values.")
        return bytes.fromhex(value)

    def process_result_value(self, value, dialect):
        return value.hex() if value else None

class Price(Base):
    __tablename__ = 'prices'

    # The id is composed by the src_chain_id followed by the dest_chain_id
    src_dest = Column(ByteHexString(2 * 32), primary_key=True)
    price = Column(Numeric(10,4), nullable=False)

class PendingRequest(Base):
    __tablename__ = 'pending_requests'

    src_payment_hash = Column(ByteHexString(32), primary_key=True)

    src_chain = Column(ByteHexString(32), nullable=False)
    src_bolt11 = Column(String(MAX_BOLT11), nullable=False)
    src_expires_at = Column(DateTime(), nullable=False)
    src_amount = Column(Integer(), nullable=False)

    dest_payment_hash = Column(ByteHexString(32), nullable=False, unique=True)
    dest_chain = Column(ByteHexString(32), nullable=False)
    dest_bolt11 = Column(String(MAX_BOLT11), nullable=False)
    dest_expires_at = Column(DateTime(), nullable=False)
    dest_amount = Column(Integer(), nullable=False)

    other_gw_payment_hash = Column(ByteHexString(32))
    other_gw_url = Column(String(MAX_URL_LEN))
    other_gw_chain = Column(ByteHexString(32))
    other_gw_bolt11 = Column(String(MAX_BOLT11))
    other_gw_expires_at = Column(DateTime())
    other_gw_amount = Column(Integer())

class PaidRequest(Base):
    __tablename__ = 'paid_requests'

    src_payment_hash = Column(ByteHexString(32), primary_key=True)

    src_chain = Column(ByteHexString(32), nullable=False)
    src_bolt11 = Column(String(MAX_BOLT11), nullable=False)
    src_expires_at = Column(DateTime(), nullable=False)
    src_payment_preimage = Column(ByteHexString(32), nullable=False)

    dest_payment_hash = Column(ByteHexString(32), nullable=False, unique=True)
    dest_chain = Column(ByteHexString(32), nullable=False)
    dest_bolt11 = Column(String(MAX_BOLT11), nullable=False)
    dest_expires_at = Column(DateTime(), nullable=False)
    dest_payment_preimage = Column(ByteHexString(32), nullable=False)

    other_gw_payment_hash = Column(ByteHexString(32))
    other_gw_url = Column(String(MAX_URL_LEN))
    other_gw_chain = Column(ByteHexString(32))
    other_gw_bolt11 = Column(String(MAX_BOLT11))
    other_gw_expires_at = Column(DateTime())
    other_gw_payment_preimage = Column(ByteHexString(32))
