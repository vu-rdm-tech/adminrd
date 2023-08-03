
import django_tables2 as tables
from django.utils.html import format_html


class ProjectTable(tables.Table):
    id = tables.Column()
    name = tables.Column()
    size = tables.Column()
    quotum = tables.Column()
    create_date = tables.Column()

    def render_id(self, value):
        return format_html(f'<a href="{value}">{value}</>')

    def render_request_date(self, value):
        return value.strftime("%Y-%m-%d")

    class Meta:
        attrs = {"class": "table"}
        template_name = "django_tables2/bootstrap4.html"


