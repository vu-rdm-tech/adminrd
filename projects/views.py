from django.shortcuts import render
from django.http import JsonResponse
from models import Project, ProjectStats, MiscStats
from datetime import datetime



# Create your views here.
def index(request):
    num_projects = Project.objects.filter(delete_date__isnull=True).all().count
    context = {
        'num_projects': num_projects,
    }
    return render(request, 'index.html', context=context)


