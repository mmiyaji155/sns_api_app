import requests
import random

client_key = 'awrf3sfxux1til3h'


def test_tiktok_request():
    base_url = 'https://www.tiktok.com/v2/auth/authorize/'
    csrfState = str(random.randint(0, 1000000))
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cache-Control': 'no-cache'
    }
    params = {
        'client_key': client_key,
        'scope': 'user.info.basic',
        'response_type': 'code',
        'redirect_uri': redirect_url,
        'state': csrfState
    }
    # SERVER_ENDPOINT_OAUTH = base_url + '?' + '&'.join([f'{key}={value}' for key, value in params.items()])
    res = requests.post(base_url, headers=headers, data=params)
    print(res)


#
# import ssl
#
# print(ssl.OPENSSL_VERSION)
# print(ssl.OPENSSL_VERSION_INFO)
#
#
#
# import sys
# print(sys.executable)






