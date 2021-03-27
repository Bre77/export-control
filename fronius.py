import requests
import re
from requests.compat import urlparse, str, basestring
from requests.cookies import extract_cookies_to_jar
from requests._internal_utils import to_native_string
from requests.utils import parse_dict_header

BASE = "http://fronius"

USERNAME = 'service'
PASSWORD = ''
EXPORT_LIMIT = 0

# Patch the HTTP Digest Auth to use the modified header
class HTTPDigestAuth(requests.auth.HTTPDigestAuth):
    def handle_401(self, r, **kwargs):
        """
        Takes the given response and tries digest-auth, if needed.

        :rtype: requests.Response
        """

        # If response is not 4xx, do not auth
        # See https://github.com/psf/requests/issues/3772
        if not 400 <= r.status_code < 500:
            self._thread_local.num_401_calls = 1
            return r

        if self._thread_local.pos is not None:
            # Rewind the file position indicator of the body to where
            # it was to resend the request.
            r.request.body.seek(self._thread_local.pos)
        s_auth = r.headers.get('X-WWW-Authenticate', '')

        if 'digest' in s_auth.lower() and self._thread_local.num_401_calls < 2:

            self._thread_local.num_401_calls += 1
            pat = re.compile(r'digest ', flags=re.IGNORECASE)
            self._thread_local.chal = parse_dict_header(pat.sub('', s_auth, count=1))

            # Consume content and release the original connection
            # to allow our new request to reuse the same one.
            r.content
            r.close()
            prep = r.request.copy()
            extract_cookies_to_jar(prep._cookies, r.request, r.raw)
            prep.prepare_cookies(prep._cookies)

            prep.headers['Authorization'] = self.build_digest_header(
                prep.method, prep.url)
            _r = r.connection.send(prep, **kwargs)
            _r.history.append(r)
            _r.request = prep

            return _r

        self._thread_local.num_401_calls = 1
        return r

with requests.session() as s:
    s.auth = HTTPDigestAuth(USERNAME,PASSWORD)
    dno = s.get(BASE+'/config/exportlimit/')
    if not dno.ok:
        exit
    print(dno.json()['Body']['Data'])
    payload = dno.json()['Body']['Data']
    payload['exportlimit']['DPL_WLIM_ABS'] = 0

    change = s.post(BASE+'/config/exportlimit/?method=save',json=payload)
    if change.ok and change.json()['Head']['Status']['Code'] == 0:
        print("Done")
    else:
        print(change.status_code)
        print(change.json()['Head']['Status'])