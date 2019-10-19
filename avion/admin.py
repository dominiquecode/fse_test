from django.contrib import admin
from .models import Bank, AircraftRetired, Aircraft, Use, Fbo, \
    Facilities, FacilitiesCost, Account, Archive, Flight

# Register your models here.
#
# class BanqueAdmin(admin.ModelAdmin):

admin.site.register(Bank)

admin.site.register(Account)


class AircraftAdmin(admin.ModelAdmin):
    model = Aircraft
    list_display = ['registration', 'makemodel', 'owner', 'home', 'location', 'actif', 'challenge']
    list_filter = ['actif']
    list_editable = ['actif']


admin.site.register(Aircraft, AircraftAdmin)

admin.site.register(AircraftRetired)

admin.site.register(Use)

admin.site.register(Fbo)

admin.site.register(Facilities)

admin.site.register(FacilitiesCost)

admin.site.register(Archive)

admin.site.register(Flight)

