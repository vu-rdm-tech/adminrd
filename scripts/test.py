import requests
from config import API_KEY

headers = {
            'Accept': 'application/json',
            'Accept-Language': 'en',
            'Authorization': f'Authorization: Bearer {API_KEY}'
            }
res = requests.get('https://vu.data.surfsara.nl/dashboard/api/functional-account/12004', headers=headers)

print(res.text)

def _do_getrequest(payload={}, url=''):
    print(url)
    headers = {
                'Accept': 'application/json',
                'Accept-Language': 'en',
                'Authorization': f'Authorization: Bearer {API_KEY}'
               }
    res = requests.get(RD_FA_URL, headers=headers)
    if res.status_code == 200:
        return res
    else:
        raise Exception('*** Got: status_code: %s' % res.status_code)
    
res=_do_getrequest(url='https://vu.data.surfsara.nl/dashboard/api/functional-account/12004')
print(res.text)