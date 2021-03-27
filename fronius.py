import requests
#import re
#from requests.cookies import extract_cookies_to_jar
#from requests.utils import parse_dict_header


from config import BASE, USERNAME, PASSWORD
EXPORT_LIMIT = 0

class FroniusAdapter(requests.adapters.HTTPAdapter):
    def build_response(self, req, resp):
        response = super().build_response(req, resp)
        if 'X-WWW-Authenticate' in response.headers:
            response.headers['WWW-Authenticate'] = response.headers['X-WWW-Authenticate']
        return response

with requests.session() as s:
    s.mount(BASE, FroniusAdapter())
    s.auth = requests.auth.HTTPDigestAuth(USERNAME,PASSWORD)
    dno = s.get(BASE+'/config/exportlimit/')
    if not dno.ok:
        print(dno.status_code)
        exit

    payload = dno.json()['Body']['Data']
    payload['exportlimit']['DPL_WLIM_ABS'] = EXPORT_LIMIT

    change = s.post(BASE+'/config/exportlimit/?method=save',json=payload)
    if change.ok and change.json()['Head']['Status']['Code'] == 0:
        print(f"Set export limit to {EXPORT_LIMIT} Watts")
    else:
        print(change.status_code)
        print(change.json()['Head']['Status'])