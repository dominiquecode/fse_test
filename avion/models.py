from django.db import models
from django.utils import timezone


class Bank(models.Model):
    # serialnumber = models.CharField(max_length=10, default=0)
    ident = models.IntegerField()
    # date_item = models.CharField(max_length=100, blank=True, null=True)
    date_item = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True)
    destinataire = models.CharField(max_length=100)
    origine = models.CharField(max_length=100)
    amount = models.FloatField()
    reason = models.CharField(max_length=100)
    fbo = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    aircraft = models.CharField(max_length=10, blank=True, null=True)
    comment = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return str(self.ident) + " Montant : " + str(self.amount)


class Banktemp(models.Model):
    # serialnumber = models.CharField(max_length=10, default=0)
    ident = models.IntegerField()
    date_item = models.CharField(max_length=100, blank=True, null=True)
    destinataire = models.CharField(max_length=100)
    origine = models.CharField(max_length=100)
    amount = models.FloatField()
    reason = models.CharField(max_length=100)
    fbo = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    aircraft = models.CharField(max_length=10, blank=True, null=True)
    comment = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return str(self.ident) + " Montant : " + str(self.amount)


class Aircraft(models.Model):
    serialnumber = models.CharField(max_length=10)
    makemodel = models.CharField(max_length=100)
    registration = models.CharField(max_length=20)
    owner = models.CharField(max_length=100)
    location = models.CharField(max_length=10)
    location_name = models.CharField(max_length=100)
    home = models.CharField(max_length=10)
    equipment = models.CharField(max_length=10)
    rental_dry = models.FloatField(blank=True, null=True)
    rental_wet = models.FloatField(blank=True, null=True)
    bonus = models.FloatField(blank=True, null=True)
    need_repair = models.IntegerField(blank=True, null=True)
    airframe_time = models.CharField(max_length=20)
    engine_time = models.CharField(max_length=20)
    last100 = models.CharField(max_length=20)
    leasedfrom = models.CharField(max_length=100)
    monthlyfee = models.FloatField(blank=True, null=True)
    feeowed = models.FloatField(blank=True, null=True)
    actif = models.BooleanField(default=True)
    challenge = models.BooleanField(default=False)

    def __str__(self):
        return self.registration + ' (' + self.makemodel + ')'


class AircraftRetired(models.Model):
    """
    Les données économiques par avion
    """
    serialnumber = models.CharField(max_length=10, default=0)
    registration = models.CharField(max_length=10)
    makemodel = models.CharField(max_length=100)
    home = models.CharField(max_length=5)
    location = models.CharField(max_length=5)
    airframe_time = models.CharField(max_length=50, default=0)
    engine_time = models.CharField(max_length=50, default=0)
    last100 = models.CharField(max_length=50, default=0)
    leasedfrom = models.CharField(max_length=100, default='N/A')
    monthlyfee = models.CharField(max_length=20, blank=True, null=True)
    motif = models.CharField(max_length=100, default='N/A')

    def __str__(self):
        return self.registration + " " + self.makemodel + "  (propriétaire : " + self.leasedfrom + ")"


class Use(models.Model):
    """
    les données d'utilisation des avions de la flotte
    """
    date_created = models.DateTimeField(blank=True, null=True)
    serialnumber = models.CharField(max_length=10, default=0)
    immat = models.CharField(max_length=10)
    type = models.CharField(max_length=50)
    gain_location = models.FloatField(default=0.0)
    gain_travail = models.FloatField(default=0.0)
    frais_entretien = models.FloatField(default=0.0)
    frais_carburant = models.FloatField(default=0.0)
    frais_vol = models.FloatField(default=0.0)
    lease = models.FloatField(default=0.0)
    frais_mensuel = models.FloatField(default=0.0)
    profits = models.FloatField(default=0.0)
    ratio_nm = models.FloatField(default=0.0)

    def __str__(self):
        return self.immat + ' (' + self.type + ')' + ' Profit : ' + str(self.profits)


class Archive(models.Model):
    """
    les données d'utilisation des avions de la flotte
    """
    date_created = models.DateTimeField(blank=True, null=True)
    serialnumber = models.CharField(max_length=10, default=0)
    immat = models.CharField(max_length=10)
    type = models.CharField(max_length=50)
    gain_location = models.CharField(max_length=50, default=0)
    gain_travail = models.CharField(max_length=50, default=0)
    frais_entretien = models.CharField(max_length=50, default=0)
    frais_carburant = models.CharField(max_length=50, default=0)
    frais_vol = models.CharField(max_length=50, default=0)
    lease = models.CharField(max_length=50, default=0)
    frais_mensuel = models.CharField(max_length=50, default=0)
    profits = models.CharField(max_length=50, default=0)
    ratio_nm = models.FloatField(default=0.0)

    def __str__(self):
        return self.immat + ' (' + self.type + ')' + ' Profit : ' + str(self.profits)


class Assignment(models.Model):
    """
    les détails de chaque assignement à suivre
    """
    ident = models.IntegerField()
    location = models.CharField(max_length=5)
    toicao = models.CharField(max_length=5)
    fromicao = models.CharField(max_length=5)
    amount = models.IntegerField(default=1)
    unittype = models.CharField(max_length=50)
    commodity = models.CharField(max_length=100)
    pay = models.FloatField(default=0)

    def __str__(self):
        return self.location


class Fbo(models.Model):
    """
    les données de suivi des FBO's
    """
    fboid = models.CharField(max_length=10)
    status = models.CharField(max_length=10)
    airport = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    owner = models.CharField(max_length=100)
    icao = models.CharField(max_length=5)
    location = models.CharField(max_length=100)
    lots = models.CharField(max_length=100)
    repairshop = models.CharField(max_length=5)
    gates = models.CharField(max_length=10)
    gatesrented = models.CharField(max_length=10)
    fuel100ll = models.CharField(max_length=10)
    fueljeta = models.CharField(max_length=10)
    buildingmaterials = models.CharField(max_length=10)
    supplies = models.CharField(max_length=10)
    suppliesperday = models.CharField(max_length=10)
    suppliedday = models.CharField(max_length=10)
    sellprice = models.CharField(max_length=50)
    rank = models.IntegerField(unique=True,blank=True,null=True)

    def __str__(self):
        return self.icao


class FboForSale(models.Model):
    """
    les données de suivi des FBO's
    """
    fboid = models.CharField(max_length=10)
    status = models.CharField(max_length=10)
    airport = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    owner = models.CharField(max_length=100)
    icao = models.CharField(max_length=5)
    location = models.CharField(max_length=100)
    lots = models.CharField(max_length=100)
    repairshop = models.CharField(max_length=5)
    gates = models.CharField(max_length=10)
    gatesrented = models.CharField(max_length=10)
    fuel100ll = models.CharField(max_length=10)
    fueljeta = models.CharField(max_length=10)
    buildingmaterials = models.CharField(max_length=10)
    supplies = models.CharField(max_length=10)
    suppliesperday = models.CharField(max_length=10)
    suppliedday = models.CharField(max_length=10)
    sellprice = models.FloatField(default=0.0)

    def __str__(self):
        return self.icao + " " + str(self.sellprice)


class FboMonth(models.Model):
    """
    les résultats mensuels des FBO de la compagnie
    """
    owner = models.CharField(max_length=50)
    icao = models.CharField(max_length=4)
    month = models.IntegerField(default=0)
    year = models.IntegerField(default=0)
    net_total = models.FloatField(default=0)
    current_ops = models.IntegerField(default=0)

    def __str__(self):
        return self.icao + ' - ' + "{:,.2f}".format(self.net_total).replace(',', ' ').replace('.', ',')


class Rank(models.Model):
    """
    l'ordre des FBO pour respecter le Texas Milk Run
    """
    num = models.IntegerField(unique=True)
    icao = models.CharField(max_length=4)

    def __str__(self):
        return str(self.num)


class Facilities(models.Model):
    """
    les données des gates de FBO (facilities)
    """
    icao = models.CharField(max_length=10)
    location = models.CharField(max_length=100)
    carrier = models.CharField(max_length=100)
    commoditynames = models.CharField(max_length=100)
    gatestotal = models.IntegerField(default=1)
    gatesrented = models.IntegerField(default=0)
    jobspublic = models.CharField(max_length=5, default='Yes')
    destinations = models.CharField(max_length=100, blank=True, null=True)
    fbo = models.CharField(max_length=100)
    status = models.CharField(max_length=50, default='')
    rentcost = models.FloatField(default=0.0, blank=True, null=True)
    buildcost = models.FloatField(default=0.0, blank=True, null=True)
    monthly_cost = models.FloatField(default=0.0, blank=True, null=True)
    incomes = models.FloatField(default=0.0)
    profits = models.FloatField(default=0.0)

    def __str__(self):
        return self.location + ' (' + self.icao + ')'


class FacilitiesCost(models.Model):
    icao = models.CharField(max_length=10)
    builtcost = models.FloatField(default=0.0, blank=True, null=True)

    def __str__(self):
        return self.icao + ' - ' + "{:,.2f}".format(self.builtcost).replace(',', ' ').replace('.', ',')


class Stat(models.Model):
    """
    les données numériques générales pour un compte particulier
    """
    account = models.CharField(max_length=100, blank=True, null=True)
    personnal_balance = models.FloatField(default=0.0)
    bank_balance = models.FloatField(default=0.0)
    flights = models.CharField(max_length=100, blank=True, null=True)
    total_miles = models.FloatField(default=0.0)
    time_flown = models.CharField(max_length=50, blank=True, null=True)
    date_created = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.account + " " + str(self.personnal_balance + self.bank_balance)


class Account(models.Model):
    """
    la définition d'un compte dans l'application
    """
    name = models.CharField(max_length=50)
    key = models.CharField(max_length=20)
    groupid = models.CharField(max_length=10, blank=True, null=True)
    group_name = models.CharField(max_length=50, blank=True, null=True)
    actif = models.BooleanField(default=True)
    nml = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Flight(models.Model):
    """
    la définition d'un vol effectué dans FSE
    """
    type = models.CharField(max_length=20)
    time = models.DateField(blank=True, null=True)
    distance = models.IntegerField()
    aircraft = models.CharField(max_length=10)
    makemodel = models.CharField(max_length=50)
    origine = models.CharField(max_length=50, blank=True, null=True)
    destination = models.CharField(max_length=50, blank=True, null=True)
    flighttime = models.TimeField(null=True, blank=True)
    income = models.FloatField(default=0.0)
    pilotfee = models.FloatField(default=0.0)
    crewcost = models.FloatField(default=0.0)
    bookingfee = models.FloatField(default=0.0)
    fuelcost = models.FloatField(default=0.0)
    groundcrewfee = models.FloatField(default=0.0)
    rentalcost = models.FloatField(default=0.0)

    def __str__(self):
        return self.aircraft + ' ' + str(self.time)


# class GroupFlight(models.Model):
#     """
#     la définition d'un groupe et des vols qui lui sont reliés
#     """
#     idflight = models.IntegerField()
#     type = models.CharField(max_length=20)
#     time = models.CharField(max_length=30,null=True, blank=True)
#     distance = models.IntegerField(null=True, blank=True)
#     pilot = models.CharField(max_length=50)
#     serialnumber = models.CharField(max_length=10)
#     aircraft = models.CharField(max_length=50)
#     makemodel = models.CharField(max_length=100)
#     origine = models.CharField(max_length=10)
#     destination = models.CharField(max_length=10)
#     totalenginetime = models.TimeField(null=True, blank=True)
#     flighttime = models.TimeField(null=True, blank=True)
#     groupname = models.CharField(max_length=100)
#     income = models.FloatField(null=True, blank=True)
#     pilotfee = models.FloatField(null=True, blank=True)
#     crewcost = models.FloatField(null=True, blank=True)
#     bookingfee = models.FloatField(null=True, blank=True)
#     bonus = models.FloatField(null=True, blank=True)
#     fuelcost = models.FloatField(null=True, blank=True)
#     gcf = models.FloatField(null=True, blank=True)
#     rentalprice = models.FloatField(null=True, blank=True)
#
#     def __str__(self):
#         return str(self.time) + " " + self.pilot
