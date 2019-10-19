from django.db import models


# Create your models here.
class Loan(models.Model):
    """
    les données d'emprunts en cours
    """
    types = (
        ('Avion', 'avion'),
        ('FBO', 'fbo'),
        ('Gates', 'gate')
    )

    modes = (
        ('M', 'mensuel'),
        ('J', '30 jours'),
        ('A', 'Autres')
    )

    etats = (
        ('En cours', 'en cours'),
        ('Terminé', 'Terminé')
    )

    type = models.CharField(max_length=10, choices=types)
    mode = models.CharField(max_length=10, choices=modes)
    amount = models.FloatField(default=0.0)
    payback = models.FloatField(default=0.0)
    finance_by = models.CharField(max_length=100, blank=True, null=True)
    date_begin = models.DateField(auto_now_add=False, auto_now=False, blank=True, null=True)
    next_date_payment = models.DateField(auto_now_add=False, auto_now=False, blank=True, null=True)
    title = models.CharField(max_length=100, blank=True, null=True, default='none')
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, blank=True, null=True, choices=etats)

    def __str__(self):
        return self.title + ' - ' + self.finance_by


class Project(models.Model):
    """
    les différents projets en cours de développement
    """
    types = (
        ('Avion', 'avion'),
        ('FBO', 'fbo'),
        ('Code', 'code'),
        ('Autres', 'autres')
    )

    title = models.CharField(max_length=100, blank=True, null=True)
    type = models.CharField(max_length=10, choices=types)
    date_begin = models.DateField(auto_created=True, auto_now=False, blank=True, null=True)
    date_end = models.DateField(auto_created=False, auto_now=False, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    amount = models.FloatField(default=0.0)

    def __str__(self):
        return self.title


class FboMonthlySummary(models.Model):
    """
    les résultats mensuels par FBO
    """
    owner = models.CharField(max_length=30)
    icao = models.CharField(max_length=10)
    month = models.IntegerField()
    year = models.IntegerField()
    ass_rental = models.FloatField(default=0.0)
    ass_income = models.FloatField(default=0.0)
    ass_pilot = models.FloatField(default=0.0)
    ass_crew = models.FloatField(default=0.0)
    ass_booking = models.FloatField(default=0.0)

    def __str__(self):
        return self.icao + ' ' + self.owner


class DvaWeek(models.Model):
    """
    les conditions de suivi de DVA
    """
    date_from = models.DateField(blank=True, null=True)
    date_to = models.DateField(blank=True, null=True)
    ident_actif = models.IntegerField(blank=True, null=True)
    week_num = models.IntegerField()
    amount = models.FloatField(default=0.0)

    def __str__(self):
        return str(self.week_num) + ' - ' + str(self.ident_actif)


# class Monthend(models.Model):
#     """
#     la description et le montant des fins de mois
#     """
#     year = models.IntegerField()
#     month = models.IntegerField()
#     aircraft_owner_fee = models.FloatField(default=0.0)
#     aircraft_lease = models.FloatField(default=0.0)
#     gate_rented = models.FloatField(default=0.0)
#     loan_current = models.FloatField(default=0.0)
#     amount = models.FloatField(default=0.0)
#
#     def __str__(self):
#         return str(self.year) + "-" + str(self.month) + " : " + str(self.amount)
