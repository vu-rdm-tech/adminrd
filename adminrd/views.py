from django.shortcuts import render
from projects.models import Project, ProjectStats, MiscStats
from datetime import datetime
from django.http import JsonResponse

start_year = 2023
today = datetime.now()
end_month = today.month
end_year = today.year

# Create your views here.
def index(request):
    miscstats = MiscStats.objects.latest('collected')
    context = {
        'num_projects': Project.objects.filter(delete_date__isnull=True).all().count,
        'num_projects_large': ProjectStats.objects.filter(size__gt = 500, collected = miscstats.collected).all().count,
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