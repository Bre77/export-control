import requests
import math
import time
from datetime import datetime

REGION = 'QLD1'
MAX_EXPORT = 5000
MIN_EXPORT = 0

payload = {'timeScale': ['5MIN']}
headers = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36'}

expected = math.floor((time.time()+150)/300)*300

with requests.Session() as s:
    while True:
        response = s.post("https://aemo.com.au/aemo/apps/api/report/5MIN", headers=headers, json=payload)
        if(response.status_code == 200):
            data = [x for x in response.json()['5MIN'] if x['REGION'] == REGION]
            received = int(datetime.strptime(data[-1]['SETTLEMENTDATE'], '%Y-%m-%dT%H:%M:%S').timestamp())-300
            if(received < expected):
                print(f"No settlement yet, request took {round(response.elapsed.total_seconds(),3)}, data may be cached until {response.headers['Expires']}")
                time.sleep(7.5)
                continue
            else:
                lag = round(time.time()-received,3)
                print(f"Got data {lag} seconds late, request took {round(response.elapsed.total_seconds(),3)} seconds, updated {response.headers['Last-Modified']}")
                break

price = (data[-1]['RRP']+data[-2]['RRP']+data[-3]['RRP']+data[-4]['RRP']+data[-5]['RRP']+data[-6]['RRP'])/6
#print(data[-1]['RRP'],data[-2]['RRP'],data[-3]['RRP'],data[-4]['RRP'],data[-5]['RRP'],data[-6]['RRP'])
#print(data[-1]['SETTLEMENTDATE'],data[-2]['SETTLEMENTDATE'],data[-3]['SETTLEMENTDATE'],data[-4]['SETTLEMENTDATE'],data[-5]['SETTLEMENTDATE'],data[-6]['SETTLEMENTDATE'])

if(price > 0):
    export = MAX_EXPORT
else:
    export = MIN_EXPORT
print(f"Export up to {export} Watts, wholesale FiT is expected to be {round(price/10,3)} c/kWh")

