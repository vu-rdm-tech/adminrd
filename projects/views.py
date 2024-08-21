from django.shortcuts import render
from django.http import JsonResponse, Http404
from .models import Project, ProjectStats, MiscStats
from datetime import datetime
from .tables import ProjectTable
from django_tables2 import RequestConfig
from .tables import ProjectTable, ProjectFilter

GB = 1024 * 1024 * 1024
start_year = 2021
today = datetime.now()
end_month = today.month
end_year = today.year
COLORSET = ['rgba(141,211,199)', 'rgba(255,255,179)', 'rgba(190,186,218)', 'rgba(251,128,114)', 'rgba(128,177,211)',
            'rgba(253,180,98)', 'rgba(179,222,105)', 'rgba(252,205,229)', 'rgba(217,217,217)', 'rgba(188,128,189)',
            'rgba(204,235,197)', 'rgba(255,237,111)']

class CustomObject():
    pass

def projects_index_table(request):
    f = ProjectFilter(request.GET, queryset=Project.objects.filter(delete_date__isnull=True).all().order_by('name'))
    data = []
    for p in f.qs:
        d = {}
        d['id'] = p.id
        d['name'] = p.name
        d['department'] = p.department.abbreviation
        d['faculty'] = p.department.faculty
        d['quotum'] = p.quotum
        d['create_date'] = p.create_date
        d['size'] = ProjectStats.objects.filter(project=p).latest('collected').size
        d['last_update'] = p.last_update
        #d = _get_rf_table(p, d)
        data.append(d)

    table = ProjectTable(data)
    RequestConfig(request, paginate={'per_page': 10}).configure(table)
    return render(request, "projects/index.html", {
        "table": table, "filter": f
    })
    
def project_detail_data(project_id):
    data = CustomObject()
    pr = Project.objects.get(pk=project_id)
    print(project_id)
    print(pr)
    data.project = pr
    data.project.size = ProjectStats.objects.filter(project=pr).latest('collected').size
    return data

def project_detail(request, project_id):
    data = project_detail_data(project_id)
    if data == None:
        raise Http404("Project does not exist")

    return render(request, 'projects/details.html', context={'data': data})

def _stats_month(project, year, month):
    return ProjectStats.objects.filter(project=project, collected__year=year,
                                        collected__month=month).order_by('collected').last()

def _monthly_stats(project):
    stats = []
    last_size = 0
    for year in range(start_year, end_year + 1):
        for month in range(1, 13):
            s = _stats_month(project, year, month)
            if s is not None:
                s.label = f'{year}-{str(month).rjust(2, "0")}'
                s.delta = s.size - last_size
                last_size = s.size
                stats.append(s)
    return stats

def project_stats(project_id):
    project = Project.objects.get(pk=project_id)
    project_stats = {}
    labels = []

    stats = _monthly_stats(project)

    # Now merge these on label
    for stat in stats:
        label = stat.label
        if label not in labels:
            labels.append(label)
        if label not in project_stats:
            project_stats[label] = {}
            project_stats[label]['size'] = 0
            project_stats[label]['delta'] = 0
        project_stats[label]['size'] += stat.size
        project_stats[label]['delta'] += stat.delta
    return sorted(labels), project_stats


def project_size_chart_json(request, project_id):
    data = []
    labels, stats = project_stats(project_id)
    print(stats)
    i = 0
    for label in labels:
        data.append(round((stats[label]['size']), 2))
        i += 1
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

def project_delta_chart_json(request, project_id):
    research = []
    vault = []
    labels, stats = project_stats(project_id)
    i = 0
    for label in labels:
        research.append(round(stats[label]['delta'], 2))
        i += 1
    datasets = [
        {
            'label': 'Usage',
            'backgroundColor': 'rgba(237, 154, 200, 0.4)',
            'borderColor': 'rgba(237, 154, 200)',
            'borderWidth': 1,
            'data': research,
        },
   ]
    return JsonResponse(data={'labels': labels, 'datasets': datasets})
