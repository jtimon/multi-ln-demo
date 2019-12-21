import time

from py_ln_gateway.db import init_db

# Wait for db to start
time.sleep(12)

init_db()
