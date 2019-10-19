from django.contrib import admin
from .models import Network, GroupFlight, Pilot


# Register your models here.
class NetworkAdmin(admin.ModelAdmin):
    model = Network
    list_display = ['name', 'hub', 'nb_fbo', 'aircraft', 'nml', 'status', 'pilot']
    list_filter = ['nml', 'status']


admin.site.register(Network, NetworkAdmin)

admin.site.register(GroupFlight)


class PilotAdmin(admin.ModelAdmin):
    model = Pilot
    list_display = ['name', 'date_inscription', 'date_depart', 'actif']
    list_filter = ['actif']
    date_hierarchy = 'date_inscription'


admin.site.register(Pilot, PilotAdmin)
