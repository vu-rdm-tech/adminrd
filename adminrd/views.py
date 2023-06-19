from django.shortcuts import render
from projects.models import Project, ProjectStats, MiscStats, Department
from datetime import datetime, timedelta
from django.http import JsonResponse
import logging
from django.utils.timezone import now, make_aware

start_year = 2023
today = datetime.now()
end_month = today.month
end_year = today.year

logger = logging.getLogger(__name__)

COLORSET = ['rgba(141,211,199)', 'rgba(255,255,179)', 'rgba(190,186,218)', 'rgba(251,128,114)', 'rgba(128,177,211)',
            'rgba(253,180,98)', 'rgba(179,222,105)', 'rgba(252,205,229)', 'rgba(217,217,217)', 'rgba(188,128,189)',
            'rgba(204,235,197)', 'rgba(255,237,111)', 'rgba(255,237,111)', 'rgba(255,237,111)', 'rgba(255,237,111)', 'rgba(255,237,111)', 'rgba(255,237,111)', 'rgba(255,237,111)', 'rgba(255,237,111)']


# Create your views here.
def index(request):
    miscstats = MiscStats.objects.latest('collected')
    cutoff = make_aware(datetime.combine(miscstats.collected, datetime.min.time())) - timedelta(days=366)
    logger.info(f'******** cutoff: {cutoff}')
    context = {
        'num_projects': Project.objects.filter(delete_date__isnull=True).all().count,
        # change date over a year ago
        'stale_projects': Project.objects.filter(last_update__lt = cutoff).all().count,
        #'stale_empty_projects': Project.objects.filter(last_update__lt = cutoff, size = 0).all().count,
        'total_size': "%3.1f" % (miscstats.size_total / 1024),
        'total_quotum': "%3.1f" % (miscstats.quotum_total / 1024),
        'num_users': miscstats.users_total,
        'last_updated': miscstats.collected,
    }
    return render(request, 'index.html', context=context)

def _quarterly_miscstats():
    quarters = [3, 6, 9, 12]
    stats = []
    for year in range(start_year, end_year + 1):
        q = 1
        for month in quarters:
            s = MiscStats.objects.filter(collected__year=year, collected__month__lte=month,
                                         collected__month__gt=month - 3).order_by('collected').last()
            if s is not None:
                s.label = f'{year}-Q{q}'
                stats.append(s)
            q += 1
    return stats

def project_chart_json(request):
    labels = []
    data = []
    miscstats = _quarterly_miscstats()
    for s in miscstats:
        labels.append(s.label)
        data.append(s.projects_total)
    datasets = [{
        'label': 'Projects',
        'backgroundColor': 'rgba(56,108,176, 0.4)',
        'borderColor': 'rgba(56,108,176)',
        'borderWidth': 1,
        'data': data
    }]
    return JsonResponse(data={'labels': labels, 'datasets': datasets})


def size_chart_json(request):
    labels = []
    data = []
    div = 1024
    stats = _quarterly_miscstats()
    for s in stats:
        labels.append(s.label)
        data.append(round(s.size_total / div, 2))
    datasets = [
        {
            'label': 'Usage',
            'backgroundColor': 'rgba(237, 154, 200, 0.4)',
            'borderColor': 'rgba(237, 154, 200)',
            'borderWidth': 1,
            'data': data,
        },
    ]
    return JsonResponse(data={'labels': labels, 'datasets': datasets})

def quotum_chart_json(request):
    labels = []
    data = []
    div = 1024
    stats = _quarterly_miscstats()
    for s in stats:
        labels.append(s.label)
        data.append(round(s.quotum_total / div, 2))
    datasets = [
        {
            'label': 'Quota',
            'backgroundColor': 'rgb(217, 248, 154, 0.4)',
            'borderColor': 'rgb(217, 248, 154)',
            'borderWidth': 1,
            'data': data,
        },
    ]
    return JsonResponse(data={'labels': labels, 'datasets': datasets})

def user_chart_json(request):
    labels = []
    internal = []
    external = []
    miscstats = _quarterly_miscstats()
    for s in miscstats:
        labels.append(s.label)
        internal.append(s.internal_users_total)
        external.append(s.external_users_total)
    datasets = [
        {
            'label': 'internal',
            'data': internal,
            'backgroundColor': 'rgba(127,201,127, 0.4)',
            'borderColor': 'rgba(127,201,127)',
            'borderWidth': 1,
        },
        {
            'label': 'external',
            'data': external,
            'backgroundColor': 'rgba(190,174,212,  0.4)',
            'borderColor': 'rgba(190,174,212)',
            'borderWidth': 1,
        },
    ]
    return JsonResponse(data={'labels': labels, 'datasets': datasets})

def faculty_chart_json(request):
    labels = []
    data = []
    index = {}
    i = 0
    colors = []
    projects = Project.objects.filter(delete_date__isnull=True).order_by('department').all()
    for project in projects:
        faculty = Department.objects.get(id=project.department.id).faculty
        if faculty=="BET" or faculty=="FEW": 
            faculty="BETA"
        if faculty=="LET" or faculty=="fGW":
            faculty="FGW"
        if faculty=="FPP" or faculty=="FBG":
            faculty="FGB"
        if faculty not in ["ACTA", "SBE", "FSW", "FGB", "FGW", "BETA","RCH", "FRT"]:
            faculty="other"
        if faculty not in labels:
            index[faculty] = i
            data.append(0)
            labels.append(faculty)
            colors.append(COLORSET[i])
            i += 1
        data[index[faculty]] += 1
    datasets = [{
        'label': 'Faculty',
        'backgroundColor': colors,
        'data': data
    }]
    return JsonResponse(data={'labels': labels, 'datasets': datasets})

def size_breakdown_chart_json(request):
    labels = ['0', '>0-10', '10-50', '50-100', '100-500', '500-1000', '>1000']	
    data = []
    collected=MiscStats.objects.latest('collected').collected
    data.append(ProjectStats.objects.filter(size = 0, collected = collected).all().count())
    data.append(ProjectStats.objects.filter(size__gt = 0, size__lte = 10, collected = collected).all().count())
    data.append(ProjectStats.objects.filter(size__gt = 10, size__lte = 50, collected = collected).all().count())
    data.append(ProjectStats.objects.filter(size__gt = 50, size__lte = 100, collected = collected).all().count())
    data.append(ProjectStats.objects.filter(size__gt = 100, size__lte = 500, collected = collected).all().count())
    data.append(ProjectStats.objects.filter(size__gt = 500, size__lte = 1000, collected = collected).all().count())
    data.append(ProjectStats.objects.filter(size__gt = 1000, collected = collected).all().count())
    
    
    datasets = [
        {
            'label': 'Size breakdown',
            'backgroundColor': 'rgb(128,177,211, 0.4)',
            'borderColor': 'rgba(128,177,211)',
            'borderWidth': 1,
            'data': data,
        },
    ]
    return JsonResponse(data={'labels': labels, 'datasets': datasets})