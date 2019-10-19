from django.contrib import admin
from finances.models import Project, Loan, DvaWeek

# Register your models here.
admin.site.register(Loan)

admin.site.register(Project)

admin.site.register(DvaWeek)