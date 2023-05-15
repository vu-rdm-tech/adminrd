from config import API_KEY, RD_FA_URL, DATA_DIR
import requests
#import requests_cache
import json
from datetime import datetime
import logging

#requests_cache.install_cache(cache_name='rd_requests_cache', allowable_methods=('GET', 'POST'))

today = datetime.now()
today_str = today.strftime('%Y%m%d')
year = today.strftime('%Y')
week = today.strftime('%U')

def setup_logging():
    LOGFILE = f'{DATA_DIR}/log/adminrd-tasks_{today.year}{today.strftime("%m")}.log'
    logger = logging.getLogger('rd_tasks')
    hdlr = logging.FileHandler(LOGFILE)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.INFO)
    return logger

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
        logger.error('Got: status_code: %s' % res.status_code)
        raise Exception('*** Got: status_code: %s' % res.status_code)


# get functional account data
def get_functional_account_data():
    logger.info(f'Do the requests')
    all_data = []
    # get totals
    page = 1
    res, cached = _do_getrequest(page=page, per_page=50, url=RD_FA_URL)
    json_data = res.json()
    last_page = json_data['meta']['last_page']
    logger.info(f'last page {last_page}')
    data = json_data['data']
    all_data.extend(data)
    while page<=last_page:
        res, cached = _do_getrequest(page=page, per_page=50, url=RD_FA_URL)
        json_data = res.json()
        data = json_data['data']
        all_data.extend(data)
        page += 1
    return all_data

logger = setup_logging()
logger.info(f'get functional account data from {RD_FA_URL}')
data = get_functional_account_data()
filename = f'{DATA_DIR}/functional_accounts_{today_str}.json'

_store(data, filename)
