
import django_tables2 as tables
from django_tables2.utils import A
from django.utils.html import format_html
from django_filters.views import FilterView
from django_filters import FilterSet
from django_tables2.views import SingleTableMixin
from projects.models import Project


class ProjectTable(tables.Table):
    
    name = tables.Column()
    department = tables.Column()
    faculty = tables.Column()
    size = tables.Column()
    quotum = tables.Column()
    create_date = tables.Column()
    last_update = tables.Column()
    id = tables.Column(orderable=False, verbose_name='')

    def render_id(self, value):
        return format_html(f'<a href="{value}">details</>')

    def render_create_date(self, value):
        return value.strftime("%Y-%m-%d")
    
    def render_last_update(self, value):
        return value.strftime("%Y-%m-%d")

    class Meta:
        attrs = {"class": "table"}
        template_name = "django_tables2/bootstrap4.html"

class ProjectFilter(FilterSet):
    class Meta:
        model = Project
        fields = {"name": ["icontains"], "department__abbreviation": ["icontains"], "department__faculty": ["icontains"]}

class FilteredProjectListView(SingleTableMixin, FilterView):
    table_class = ProjectTable
    model = Project
    template_name = "projects/index.html"

    filterset_class = ProjectFilter
