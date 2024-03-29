from config import API_KEY, RD_FA_URL, DATA_DIR
import requests
import requests_cache
import json
from datetime import datetime, timedelta
import logging

requests_cache.install_cache(cache_name='rd_requests_cache', allowable_methods=('GET', 'POST'), expire_after=timedelta(hours=1))

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

def _do_getrequest(payload={}, url=''):
    print(url)
    headers = {
                'Accept': 'application/json',
                'Accept-Language': 'en',
                'Authorization': f'Authorization: Bearer {API_KEY}',
            }
    res = requests.get(url, headers=headers, params=payload)
    try:
        cached = res.from_cache
        print('******cached')
    except:
        cached = False
    if res.status_code == 200:
        return res, cached
    else:
        logger.error('Got: status_code: %s' % res.status_code)
        raise Exception('*** Got: status_code: %s' % res.status_code)


# get functional account data
def get_functional_account_data():
    adminrecords = []
    userlist = []
    logger.info('Do the requests')
    # get totals
    page = 1
    res, cached = _do_getrequest(payload = {'per_page': 50, 'page': page}, url=RD_FA_URL)
    json_data = res.json()
    last_page = json_data['meta']['last_page']
    logger.info(f'last page {last_page}')
    data = json_data['data']
    while page <= last_page:
        for d in data:
            res2, cached = _do_getrequest(url=f'{RD_FA_URL}/{d["id"]}/')
            fa_data = res2.json()['data']
            if d['id']==fa_data['id']:
                record = {
                    "rdid": fa_data['id'],
                    "name": fa_data['name'],
                    "owner_name": d['owner_name'], # seems wrong?
                    "description": fa_data['description'],
                    "last_login": fa_data.get('last_login'),
                    "status": fa_data['status']['value'],
                    "create_date": fa_data['create_date'],
                    "change_date": fa_data['change_date'],
                    "end_date": fa_data['end_date'],
                    "costcenter": fa_data['costcenter'],
                    "usage": fa_data['storage']['usage']['value'],
                    "quotum": fa_data['storage']['quotum']['value'],
                    "last_update": fa_data['storage']['last_update'],
                    "owner":   {}
                }
                users = 0
                internal_users = 0
                external_users = 0
                for account in fa_data['memberships']:
                    if account['username'] not in userlist:
                        userlist.append(account['username'])
                    if account['username'].endswith('vu.nl') or account['username'].endswith('acta.nl'):
                        internal_users += 1
                    else:
                        external_users += 1
                    if account['name'] == d['owner_name']:
                        record['owner']['rdid'] = account['id']
                        record['owner']['name'] = account['name']
                        record['owner']['username'] = account['username']
                        record['owner']['email'] = account['email']
                        record['owner']['backend'] = account['backend']
                        record['owner']['last_login'] = account['last_login']
                        record['owner']['status'] = account['status']['value']
                record['internal_users'] = internal_users
                record['external_users'] = external_users
            else:
                print(f'got wrong account {fa_data["id"]} for {d["id"]}')
                quit()

            adminrecords.append(record)
        page += 1
        res, cached = _do_getrequest(payload = {'per_page': 50, 'page': page}, url=RD_FA_URL)
        json_data = res.json()
        data = json_data['data']

    total_internal_members = 0
    total_external_members = 0
    total_functional_members = 0
    for user in userlist:
        if user.endswith('@vu.nl'):
            total_internal_members += 1
        elif '@' in user:
            total_external_members += 1
        else:
            total_functional_members += 1     
    miscstats = {
        'total_internal_members': total_internal_members,
        'total_external_members': total_external_members,
        'total_functional_members': total_functional_members,
        'userlist': userlist
    }
    return adminrecords, miscstats

logger = setup_logging()
logger.info(f'get functional account data from {RD_FA_URL}')
adminrecords, miscstats = get_functional_account_data()
data = {
    'data': adminrecords,
    'collected': today_str,
    'miscstats': miscstats
}
filename = f'{DATA_DIR}/rdprojects_{today_str}.json'

_store(data, filename)
logger.info(f'Results stored as {filename}')
