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

def process_rd_stats():
    files = sorted(os.listdir(DATADIR))
    logger.info(f'listing of datadir: [{", ".join(files)}]')
    cnt = 0
    for file in files:
        if file.startswith('rdprojects_'):
            cnt = cnt + 1
            logger.info(f'processing {file}')
            with open(f'{DATADIR}/{file}', 'r') as fp:
                data = json.load(fp)
                try:
                    filedate_str = data['collected']
                except:
                    # old style
                    filedate_str = os.path.splitext(file)[0].split('_')[1]
                filedate = datetime.strptime(filedate_str, '%Y%m%d').date()
                
                for fa in data:
                    print(f'**************** {fa["name"]}')
                    if fa['status'] == 'active':
                        #owner_name
                        owner, created = User.objects.get_or_create(rdid=fa['owner']['rdid'])
                        owner.username = fa['owner']['username']
                        owner.name = fa['owner']['name']
                        owner.email = fa['owner']['email']
                        owner.backend = fa['owner']['backend']['value']
                        owner.status = fa['owner']['status']
                        owner.last_login = datetime.strptime( fa['owner']['last_login'], '%Y-%m-%d %H:%M:%S').astimezone(tz)
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
                        #2023-05-30 16:32:45

                        project.change_date = datetime.strptime(fa['change_date'], '%Y-%m-%d %H:%M:%S').astimezone(tz)
                        if not fa['end_date'] is None:
                            project.end_date = datetime.strptime(fa['end_date'], '%Y-%m-%d %H:%M:%S').astimezone(tz)
                        project.quotum = fa['quotum']
                        project.owner_name = owner
                        project.budget = budget
                        project.department = department
                        
                        project.save()

                        stats = ProjectStats.objects.get_or_create(collected=filedate, project=project, defaults={
                            'size': fa['usage'],
                            'quotum': fa['quotum']
                        })
            shutil.move(f'{DATADIR}/{file}', f'{DATADIR}/archive/{file}')


#process_rd_stats()