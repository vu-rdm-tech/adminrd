from config import API_KEY, RD_FA_URL
import requests
import requests_cache
import json
from datetime import datetime

#requests_cache.install_cache(cache_name='rd_requests_cache', allowable_methods=('GET', 'POST'))

def _store(data, filename):
    '''
    Store the data dict as a json file

    :param data: dict
    :param filename: string
    :return:
    '''
    with open(filename, 'w') as f:
        json.dump(data, f, indent=1)

def _do_getrequest(page=1, per_page=50, url=''):
    headers = {'Content-Type': 'application/json', 
                'Accept': 'application/json',
                'Accept-Language': 'en',
                'Authorization': f'Authorization: Bearer {API_KEY}'
               }
    payload = {
        'per_page': per_page,
        'page': page
    }
    res = requests.get(RD_FA_URL, headers=headers, params=payload)
    try:
        cached = res.from_cache
    except:
        cached = False
    if res.status_code == 200:
        return res, cached
    else:
        raise Exception('*** Got: status_code: %s' % res.status_code)


# get functional account data
def get_functional_account_data():
    all_data = []
    # get totals
    page = 1
    res, cached = _do_getrequest(page=page, per_page=50, url=RD_FA_URL)
    json_data = res.json()
    last_page = json_data['meta']['last_page']
    data = json_data['data']
    all_data.extend(data)
    while page<=last_page:
        res, cached = _do_getrequest(page=page, per_page=50, url=RD_FA_URL)
        json_data = res.json()
        data = json_data['data']
        all_data.extend(data)
        page += 1
    return all_data

today = datetime.now()
today_str = today.strftime('%Y%m%d')
data = get_functional_account_data()
filename = f'data/functional_accounts_{today_str}.json'

_store(data, filename)
