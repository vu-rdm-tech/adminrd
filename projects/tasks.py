import json
import os
import re
import shutil
from datetime import datetime, timedelta, date
import logging
from projects.models import Project, User, Department, Budget, MiscStats, ProjectStats
from django.utils.timezone import now, make_aware
from django.db.models.base import ObjectDoesNotExist
from pytz import timezone

DATADIR=os.environ.get('DATADIR') # set via docker-compose
logger = logging.getLogger(__name__)
tz = timezone('Europe/Amsterdam')


def _store_fa_data(fa, collected):
    owner, created = User.objects.get_or_create(rdid=fa['owner']['rdid'])
    owner.username = fa['owner']['username']
    owner.name = fa['owner']['name']
    owner.email = fa['owner']['email']
    owner.backend = fa['owner']['backend']['value']
    owner.status = fa['owner']['status']
    try:
        owner.last_login = datetime.strptime( fa['owner']['last_login'], '%Y-%m-%d %H:%M:%S').astimezone(tz)
    except:
        owner.last_login = None
    owner.save()
    
    #department
    # SBE_FIN_Sustainable_Investments
    tmp = fa['name'].split('_')
    if len(tmp) >= 3:
        faculty = tmp[0]
        abbreviation = tmp[1]
    else:
        faculty = 'unknown'
        abbreviation = 'unknown'
    department, created = Department.objects.get_or_create(faculty=faculty, abbreviation=abbreviation)
    department.save
    
    #budget
    if fa['costcenter'] is None:
        cc = 'unknown'
    else: 
        cc = fa['costcenter']
    budget, created = Budget.objects.get_or_create(code=cc)
    if created: # do not overwrite manually corrected values
        budget.type = 'u'
        budget.vunetid = 'xxx123'
    budget.save()

    project, created = Project.objects.get_or_create(rdid=fa['rdid'], defaults = {
        'create_date': datetime.strptime(fa['create_date'], '%Y-%m-%d %H:%M:%S').astimezone(tz)
    })
    project.name = fa['name']
    project.description = fa['description']
    try: # fields missing in first exports
        project.internal_users = fa['internal_users']
        project.external_users = fa['external_users']
    except:
        pass
    try:
        project.last_update = datetime.strptime(fa['last_update'], '%Y-%m-%d %H:%M:%S').astimezone(tz)
    except:
        pass
    
    project.change_date = datetime.strptime(fa['change_date'], '%Y-%m-%d %H:%M:%S').astimezone(tz)
    if not fa['end_date'] is None:
        project.end_date = datetime.strptime(fa['end_date'], '%Y-%m-%d').astimezone(tz)
    project.quotum = fa['quotum']
    project.owner_name = owner
    project.budget = budget
    project.department = department
    project.save()

    ProjectStats.objects.get_or_create(collected=collected, project=project, defaults={
        'size': fa['usage'],
        'quotum': fa['quotum']
    })


def process_rd_stats():
    files = sorted(os.listdir(DATADIR))
    logger.info(f'listing of datadir: [{", ".join(files)}]')
    cnt = 0
    for file in files:
        if file.startswith('rdprojects_'):
            cnt = cnt + 1
            logger.info(f'processing {file}')
            with open(f'{DATADIR}/{file}', 'r') as fp:
                js = json.load(fp)
                try:
                    collected = datetime.strptime(js['collected'], '%Y%m%d').date()
                    data = js['data']
                    miscstats = js['miscstats']
                except:
                    # old style
                    filedate_str = os.path.splitext(file)[0].split('_')[1]
                    collected = datetime.strptime(filedate_str, '%Y%m%d').date()
                    data = js
                    miscstats = {
                        'total_internal_members': 0,
                        'total_external_members': 0,
                        'total_functional_members': 0
                    }
                
                size_total = 0
                projects_total = 0
                users_total = 0
                internal_users_total = 0
                external_users_total = 0
                quotum_total = 0
                for fa in data:
                    if fa['status'] == 'active':
                        if fa['owner']:
                            _store_fa_data(fa=fa, collected=collected)
                            quotum_total += fa['quotum']
                            size_total += fa['usage']
                            projects_total += 1
                        else:
                            logger.error(f'{fa["rdid"]} - {fa["name"]} has no owner.')
                MiscStats.objects.update_or_create(collected = collected, defaults={
                    'size_total': size_total,
                    'quotum_total': quotum_total,
                    'users_total': miscstats['total_internal_members'] + miscstats['total_external_members'],
                    'internal_users_total': miscstats['total_internal_members'],
                    'external_users_total': miscstats['total_external_members'],
                    'projects_total': projects_total
                })

            shutil.move(f'{DATADIR}/{file}', f'{DATADIR}/archive/{file}')


#process_rd_stats()