from py_ln_gateway import db

class Price(db.Model):
    __tablename__ = 'prices'

    id = db.Column(db.Integer, primary_key=True)

    # FIX optimization: binascii.unhexlify and store 32 bytes instead of 64 char hex string
    # FIX make src_chain and dest_chain unique together and the id, and have a getter
    src_chain = db.Column(db.String(64))
    dest_chain = db.Column(db.String(64))
    price = db.Column(db.Numeric(10,4))
