from django.contrib import admin
from .models import Project, ProjectStats, User, Department
# Register your models here.


admin.site.register(Project)
admin.site.register(ProjectStats)
admin.site.register(User)
admin.site.register(Department)
