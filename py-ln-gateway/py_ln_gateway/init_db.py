
from py_ln_gateway.app import app
from py_ln_gateway.db import db
from py_ln_gateway.models import Price

app.app_context().push()

db.create_all()

# TODO Run from a cron job like if it was pulling data from an exchange or something.
# Alternatively expose an authenticated API to update prices so that it can
# be used to update prices continuously by calling or subscribing
# to an external API. And call that instead of running this.
db.session.add(Price(
    src_chain = '58ebd25d25b128530d4d462c65a7e679b7e053e6f25ffb8ac63bc68832fda201',
    dest_chain = 'e07d79a4f8f1525814e421eb71aa9527fe8a25091fe1b9c5c312939c887aadc7',
    price = 1))
db.session.commit()
