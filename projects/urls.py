from django.urls import path

from . import views

urlpatterns = [
    path('', views.projects_index_table, name='projects_index'),
    path('<int:project_id>', views.project_detail, name='project_detail'),
    path('project_size_chart_json/<int:project_id>', views.project_size_chart_json, name='project_size_chart_json'),
    path('project_delta_chart_json/<int:project_id>', views.project_delta_chart_json, name='project_delta_chart_json'),
]