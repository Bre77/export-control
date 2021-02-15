import requests
import math
import time
from datetime import datetime

REGION = 'QLD1'

payload = {'timeScale': ['5MIN']}
headers = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36'}

expected = math.floor((time.time()+150)/300)*300

while True:
    response = requests.post("https://aemo.com.au/aemo/apps/api/report/5MIN", headers=headers, json=payload)
    if(response.status_code == 200):
        qld = [x for x in response.json()['5MIN'] if x['REGION'] == REGION]
        received = int(datetime.strptime(qld[-1]['SETTLEMENTDATE'], '%Y-%m-%dT%H:%M:%S').timestamp())-300
        if(received < expected):
            print(f"No settlement yet, request took {round(response.elapsed.total_seconds(),3)}, data may be cached until {response.headers['Expires']}")
            time.sleep(7.5)
            continue
        else:
            lag = round(time.time()-received,3)
            print(f"Got data {lag} seconds late, request took {round(response.elapsed.total_seconds(),3)} seconds, updated {response.headers['Last-Modified']}")
            break

price = (qld[-1]['RRP']+qld[-2]['RRP']+qld[-3]['RRP']+qld[-4]['RRP']+qld[-5]['RRP']+qld[-6]['RRP'])/6
print(qld[-1]['SETTLEMENTDATE'],qld[-2]['SETTLEMENTDATE'],qld[-3]['SETTLEMENTDATE'],qld[-4]['SETTLEMENTDATE'],qld[-5]['SETTLEMENTDATE'],qld[-6]['SETTLEMENTDATE'])
print(price)

if(price > 0):
    print("Export up to 5kWh")
else:
    print("Export up to 0kWh")


