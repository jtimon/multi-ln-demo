
py_gateway: export FLASK_ENV=development export LC_ALL=C.UTF-8 export LANG=C.UTF-8 export FLASK_APP=/wd/py-ln-gateway/py_ln_gateway/app.py ; export FLASK_RUN_HOST=0.0.0.0 ; flask run

gw_update_price: python3 /wd/py-ln-gateway/py_ln_gateway/cron/update_price.py

gw_clean_pending: python3 /wd/py-ln-gateway/py_ln_gateway/cron/cleanup_pending_requests.py
