from SageApi import SageApi
from DolibarrApi import DolibarrApi
from dotenv import load_dotenv
from os import getenv
import logging
import datetime


logging.basicConfig(level=logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.ERROR)
logging.getLogger("requests_oauthlib").setLevel(logging.ERROR)

load_dotenv()

s_api = SageApi(getenv('CLIENT_ID'), getenv('CLIENT_SECRET'), getenv('REDIRECT_URI'))
d_api = DolibarrApi(getenv('DOLIBARR_URL'), getenv('DOLIBARR_API_KEY'))

with open("lastrun.txt", "r") as fh:
    lastrun = fh.readline()

from sync import sync_products, sync_services, sync_contacts, sync_purchase_invoices, sync_sales_invoices, sync_sales_quotes

sync_products(s_api, d_api, lastrun)
sync_services(s_api, d_api, lastrun)
sync_contacts(s_api, d_api, lastrun)
sync_purchase_invoices(s_api, d_api, lastrun)
sync_sales_invoices(s_api, d_api, lastrun)
sync_sales_quotes(s_api, d_api, lastrun)

lastrun = datetime.datetime.now().isoformat()[:-7]
with open("lastrun.txt", "w") as fh:
    lastrun = fh.write(lastrun)
