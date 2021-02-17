import requests
import math
import time
from datetime import datetime

REGION = 'QLD1'
MAX_EXPORT = 5
MIN_EXPORT = 0

payload = {'postcode': '4209'}
#headers = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36'}

expected = math.floor((time.time()+150)/300)*300

response = requests.post("https://api.amberelectric.com.au/prices/listprices", json=payload)
if(response.status_code == 200):
    data = [x for x in response.json()['data']['variablePricesAndRenewables'] if x['periodType'] == 'ACTUAL']
    print(data[-1]['period'],data[-1]['periodSource'],data[-1]['wholesaleKWHPrice'])