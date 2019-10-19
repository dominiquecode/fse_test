# les outils de l'application Finances
from django.utils import timezone
import time, datetime
from avion.tools import *
from finances.models import Loan, Project, DvaWeek
from avion.models import Bank


class Calcul:

    def __init__(self):
        self.test = ('test', 'autre')

    def get_test(self):
        return self.test

    def get_month_end(self, year=None, month=None):
        if year is None:
            year = timezone.now().year
        if month is None:
            mont = timezone.now().month

        owner_monthly_fee = ManageAircrafts().get_total_monthly_fee()
        current_loan_fee = ManageLoan().get_actual_pay_back()

        return owner_monthly_fee


class ManageLoan:

    def __init__(self):
        self.loan_list = Loan.objects.all()
        self.loan_actif = Loan.objects.filter(status='En cours')
        self.loan_terminated = Loan.objects.filter(status='Terminé')

    def get_loan_list(self):
        return self.loan_list

    def get_loan_actif(self):
        return self.loan_actif

    def get_loan_terminated(self):
        return self.loan_terminated

    def get_actual_pay_back(self):
        total = 0.0
        for loan in self.loan_list:
            total += loan.payback

        return total

    def get_total_loan(self):
        total = 0.0
        for loan in self.loan_list:
            total += loan.amount

        return total

    def get_total_payback_actif(self):
        total = 0.0
        for loan in self.loan_actif:
            total += loan.payback

        return total

    def get_total_payback_terminated(self):
        total = 0.0
        for loan in self.loan_terminated:
            total += loan.payback

        return total

    def get_total_du(self):
        return self.get_total_loan() - self.get_actual_pay_back()


class ManageFboFinance:

    def __init__(self):
        pass

    def get_fbo_finance(self, icao, month=None, year=None):
        """
        retourne les résultats financiers d'un FBO pour un mois particulier
        :param icao: l'identifiant du FBO (code ICAO)
        :param month: le mois actuel par défaut
        :param year: l'année actuelle par défaut
        :return:
        """


class ManageDVA:

    def __init__(self):
        self._dva_week = DvaWeek.objects.all()

    def get_all_dva_weeks(self):
        return self._dva_week.order_by('ident_actif')

    def update_amount(self):
        pass

    def get_weeks_from(self, year=timezone.now().year, month=timezone.now().month, day=timezone.now().day):
        md = datetime.date(year, month, day)
        dt = DvaWeek.objects.all().order_by('date_from').filter(date_from__gte=md)

        if dt:
            for d in dt:
                print(f"Période : du {d.date_from} au {d.date_to} - montant {d.amount}")
        else:
            print(f"Aucune donnée pour cette date ({md})")

    def get_weeks_range(self,
                            yeardeb = timezone.now().year, monthdeb = timezone.now().month, daydeb = timezone.now().day,
                            yearend = timezone.now().year, monthend = timezone.now().month, dayend = timezone.now().day):
        datedeb = datetime.date(yeardeb, monthdeb, daydeb)
        dateend = datetime.date(yearend, monthend, dayend)
        jobs = DvaWeek.objects.filter(date_from__range=(datedeb, dateend))

        if jobs:
            for d in jobs:
                print(f"Période : du {d.date_from} au {d.date_to} - montant {d.amount}")
        else:
            print(f"Aucune donnée pour la période du {datedeb} au {dateend}")


