from django.db import models
from django.utils import timezone
from avion.models import Aircraft


Status = [('CONST', 'On build'),
          ('PUBLIC', 'Public use'),
          ('AVAILABLE', 'Available'),
          ('PRIVATE', 'Private use'),
          ('ON USE', 'NML use'),
          ]


class Pilot(models.Model):
    name = models.CharField(max_length=100)
    date_inscription = models.DateField(auto_created=timezone.now())
    date_depart = models.DateField(null=True, blank=True)
    actif = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Network(models.Model):
    name = models.CharField(max_length=100)
    hub = models.CharField(max_length=50, null=True, blank=True)
    nb_fbo = models.IntegerField(default=0)
    # aircraft = models.CharField(max_length=50, null=True, blank=True)
    aircraft = models.ForeignKey(Aircraft, on_delete=models.CASCADE, null=True, blank=True)
    nml = models.BooleanField(default=False)
    status = models.CharField(choices=Status, max_length=50, null=True, blank=True)
    comment = models.CharField(max_length=200, null=True, blank=True)
    pilot = models.ForeignKey(Pilot, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name + "  (NML :" + str(self.nml) + ")"


class GroupFlight(models.Model):
    """
    la définition d'un groupe et des vols qui lui sont reliés
    """
    idflight = models.IntegerField()
    type = models.CharField(max_length=20)
    time = models.DateField(null=True, blank=True)
    distance = models.IntegerField(null=True, blank=True)
    pilot = models.CharField(max_length=50)
    serialnumber = models.CharField(max_length=10)
    aircraft = models.CharField(max_length=50)
    makemodel = models.CharField(max_length=100)
    origine = models.CharField(max_length=10, null=True, blank=True)
    destination = models.CharField(max_length=10, null=True, blank=True)
    totalenginetime = models.TimeField(null=True, blank=True)
    flighttime = models.TimeField(null=True, blank=True)
    groupname = models.CharField(max_length=100, null=True, blank=True)
    income = models.FloatField(null=True, blank=True)
    pilotfee = models.FloatField(null=True, blank=True)
    groupfee = models.FloatField(null=True, blank=True)
    repartition_group = models.FloatField(default=0.0, null=True, blank=True)
    crewcost = models.FloatField(null=True, blank=True)
    bookingfee = models.FloatField(null=True, blank=True)
    bonus = models.FloatField(null=True, blank=True)
    fuelcost = models.FloatField(null=True, blank=True)
    gcf = models.FloatField(null=True, blank=True)
    rentalprice = models.FloatField(null=True, blank=True)

    def __str__(self):
        return str(self.time) + " " + self.pilot
