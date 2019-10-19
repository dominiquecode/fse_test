# -*- coding: utf-8 -*-

from urllib.request import urlopen
import xmltodict, time
from .models import Bank, Aircraft, Use, Fbo, \
    Assignment, Facilities, Stat, Rank, Account, \
    FacilitiesCost, Flight, FboMonth, FboForSale
from finances.models import FboMonthlySummary
from network.models import GroupFlight
from finances.models import DvaWeek
from django.db.models import Sum, Q, Max, Min
from django.utils import timezone
import datetime
import time

# CLASSES UTILITAIRES #
message = "Problème de connexion avec le serveur FSE "


# Class outils pour obtenir tous les comptes de l'application
class Accounts:
    """
    Retourne un dictionnaire avec tous les comptes de la compagnie
    """

    def __init__(self):
        self._account = Account.objects.filter(actif=True)
        self._list_accounts = []
        self._list_name_accounts = []
        self._list_name_accounts_nml = []
        self._list_name_accounts_no_nml = []
        self._list_keys = []

    def get_accounts(self):
        return self._account

    def get_list_account_name(self):
        for k in self.get_accounts():
            if k.group_name:
                self._list_name_accounts.append(k.name)

        return self._list_name_accounts

    def get_list_account_name_no_nml(self):
        for k in self.get_accounts().filter(Q(nml=False) & Q(name__contains='GaugauAir')):
            if k.group_name:
                self._list_name_accounts_no_nml.append(k.name)

        return self._list_name_accounts_no_nml

    def get_list_account_name_nml(self):
        for k in self.get_accounts().filter(nml=True):
            if k.group_name:
                self._list_name_accounts_nml.append(k.name)

        return self._list_name_accounts_nml

    def get_list_accounts(self):
        for k in self.get_accounts():
            self._list_accounts.append(k)

        return self._list_accounts

    def get_key_of(self, account):
        ac = self.get_accounts().get(name=account)
        if ac:
            # print(ac.name)
            return ac.key
        else:
            return None

    def get_groupid_of(self, account):
        ac = self.get_accounts().get(name=account)
        if ac:
            return ac.groupid
        else:
            return None


class Jobs:
    """
    la liste des jobs externes volés par domfse ou GaugauAir
    """

    def __init__(self):
        self._jobs = {'a2b': 'A2B Ferry Services',
                      'dva': 'Dear Valley Aviation',
                      'sda': 'Smoking Dog Aviation',
                      'cp': 'Crosspoint Air (South America)',
                      'sion': 'SION AIRWAYS',
                      }
        self.list_jobs = self._get_list_jobs()

    def get_jobs(self):
        return self._jobs

    def _get_list_jobs(self):
        listjobs = []
        for val in self._jobs.values():
            listjobs.append(val)

        return listjobs


# classe d'extraction générale des données à partir du site fse
class ExtractionDatas:
    """
    Établir une connexion avec le serveur fse
    à partir d'une URL (requête)
    de la clef d'un compte (domfse ou GaugauAir)
    pour un mois et une année particulière
    (valeur par défaut : mois=8, année=2018

    """

    def __init__(self, data_type, account='domfse', month=None, year=None, registration=None, icao=None):

        # les comptes d'utilisationk
        self.accounts = Accounts().get_accounts()
        # les variables de travail de la classe
        self.data_type = data_type
        self.account = account
        # si le paramètre de mois n'est pas précisé, on utilise le mois du jour par defaut
        if not month:
            month = timezone.now().month
        self.month = month
        # si le paramètre d'année n,est pas précisé, on utilise l'année du jour par defaut
        if not year:
            year = timezone.now().year
        self.year = year
        self.icao = icao
        self.registration = registration
        self.key = Accounts().get_key_of(self.account)
        self.facilities_string = icao
        self.url = self._build_url()

    def _build_url(self):
        """
        construire l'URL utilisée par la requête sur le serveur de FSE

        :return: la requête sous forme de chaine de caractère
        """

        if self.data_type == 'bank':
            if self.account == 'domfse':
                self.url = 'http://server.fseconomy.net/data?userkey=E5VXW4KYE0' + \
                           '&format=xml&query=payments&search=monthyear&readaccesskey=' + \
                           self.key + '&month=' + str(self.month) + '&year=' + str(self.year)
            else:
                self.url = 'http://server.fseconomy.net/data?servicekey=EF1387591' + \
                           '&format=xml&query=payments&search=monthyear&readaccesskey=' + \
                           self.key + '&month=' + str(self.month) + '&year=' + str(self.year)

        elif self.data_type == 'aircrafts':
            self.url = 'http://server.fseconomy.net/data?servicekey=EF1387591' + \
                       '&format=xml&query=aircraft&search=ownername&ownername=' + self.account
        elif self.data_type == 'facilities':
            self.url = 'http://server.fseconomy.net/data?servicekey=EF1387591' + \
                       '&format=xml&query=Facilities&search=key&readaccesskey=' + self.key
        elif self.data_type == 'fbo_month':
            self.url = 'http://server.fseconomy.net/data?userkey=E5VXW4KYE0' + \
                       '&format=xml&query=fbos&search=monthlysummary&readaccesskey=' + self.account + \
                       '&month=' + str(self.month) + '&year=' + str(self.year) + '&icao=' + self.icao
        elif self.data_type == 'stat':
            self.url = 'http://server.fseconomy.net/data?servicekey=EF1387591' + \
                       '&format=xml&query=statistics&search=key&readaccesskey=' + self.key
        elif self.data_type == 'fbo':
            self.url = 'http://server.fseconomy.net/data?servicekey=EF1387591' + \
                       '&format=xml&query=fbos&search=key&readaccesskey=' + self.key

        elif self.data_type == 'fbo_sale':
            self.url = 'http://server.fseconomy.net/data?servicekey=EF1387591&format=xml&query=fbos&search=forsale'

        elif self.data_type == 'jobsto':
            self.url = 'http://server.fseconomy.net/data?userkey=E5VXW4KYE0' + \
                       '&format=xml&query=icao&search=jobsto&icaos=' + self.facilities_string

        elif self.data_type == 'flights':
            if self.registration is not None:
                self.url = 'http://server.fseconomy.net/data?servicekey=EF1387591' + \
                           '&format=xml&query=flightlogs&search=monthyear&aircraftreg=' + self.registration + \
                           '&month=' + str(self.month) + '&year=' + str(self.year)
            else:
                self.url = ''
        elif self.data_type == 'network':
            self.url = 'http://server.fseconomy.net/data?servicekey=EF1387591' + \
                       '&format=xml&query=flightlogs&search=monthyear&readaccesskey=' + self.key + \
                       '&month=' + str(self.month) + '&year=' + str(self.year)

        elif self.data_type == 'fbo_monthly_summary':
            self.url = 'http://server.fseconomy.net/data?servicekey=EF1387591' + \
                       '&format=xml&query=fbos&search=monthlysummary&readaccesskey=' + self.account + \
                       '&month=' + str(self.month) + '&year=' + str(self.year) + '&icao=' + self.icao

        # tous les assignments publics. la clef est la liste formatée des fbos
        elif self.data_type == 'jobsfrom':
            self.url = 'http://server.fseconomy.net/data?servicekey=EF1387591' + \
                       '&format=xml&query=icao&search=jobsfrom&icaos=' + self.facilities_string

        # tous les assignments private et domfse/myflight. la clef est le nom du groupe
        elif self.data_type == 'group_assignments':
            self.url = 'http://server.fseconomy.net/data?servicekey=EF1387591' + \
                       '&format=xml&query=assignments&search=key&readaccesskey=' + self.key

        # elif self.data_type == "dva":
        #     self.url = 'http://server.fseconomy.net/data?servicekey=EF1387591&format=xml' + \
        #                '&query=payments&search=monthyear&readaccesskey=E5VXW4KYE0' + \
        #                '&month=' + str(self.month) + '&year=' + str(self.year)

        return self.url

    # TODO 18-11-09 dominiqueIMac: comment arrêter la procédure si les datas sont inexistantes pour un compte particulier
    def get_datas(self):
        """
        connecte le serveur fse avec l'URL et retourne les données
        sous forme de liste

        :param:
        :return: les données recherchées sous forme d'une liste
        """
        try:
            file = urlopen(self.url)
            data = file.read()
            file.close()
            dico = xmltodict.parse(data)
            enr = ()
            # vérifier la présence d'éléments dans la liste
            if self.data_type == 'bank':
                enr = dico['PaymentsByMonthYear']['Payment']
            elif self.data_type == 'aircrafts':
                enr = dico['AircraftItems']['Aircraft']
            elif self.data_type == 'facilities':
                if dico['FacilityItems']['@total'] == '0':
                    return None
                enr = dico['FacilityItems']['Facility']
            elif self.data_type == 'fbo':
                if dico['FboItems']['@total'] == '0':
                    return None
                enr = dico['FboItems']['FBO']
            elif self.data_type == 'fbo_sale':
                if dico['FboItems']['@total'] == '0':
                    return None
                enr = dico['FboItems']['FBO']
            elif self.data_type == 'fbo_month':
                # if dico['FboMonthlySummaryItems']['FboMonthlySummary'] == '0':
                #     return None
                enr = dico['FboMonthlySummaryItems']['FboMonthlySummary']
                # print(type(enr))

            elif self.data_type == 'stat':
                enr = dict(dico['StatisticItems']['Statistic'])

            elif self.data_type == 'jobsto':
                if dico['IcaoJobsTo']['@total'] == '0':
                    return None
                enr = dico['IcaoJobsTo']['Assignment']
            elif self.data_type == 'jobsfrom':
                if dico['IcaoJobsFrom']['@total'] == '0':
                    return None
                enr = dico['IcaoJobsFrom']['Assignment']
            elif self.data_type == 'flights':
                if dico['FlightLogsByMonthYear']['@total'] == '0':
                    return None
                enr = dico['FlightLogsByMonthYear']['FlightLog']
            elif self.data_type == 'network':
                enr = dico['FlightLogsByMonthYear']['FlightLog']
            elif self.data_type == 'fbo_monthly_summary':
                enr = dico['FboMonthlySummaryItems']['FboMonthlySummary']
            elif self.data_type == 'group_assignments':
                enr = dico['AssignmentItems']['Assignment']

            return enr

        except ValueError as ex:
            print("Erreur d'extraction de données", str(ex.args))
        except KeyError as kx:
            # print(f"Pas de données pour {self.data_type} {self.account}", str(kx))
            return


# Class nettoyage des tables locales
class CleanDBObject:
    """
    Procedure to delete all data rows in a table
    data_type are : 'aircraft', 'fbo', 'facilities', 'jobsto', 'jobsfrom', 'stat', 'use'

    """

    def __init__(self, data_type):
        self.data_type = data_type
        self.datas = self._find_object()

    def _find_object(self):
        if self.data_type == 'aircrafts':
            self.datas = Aircraft.objects.all()
        elif self.data_type == 'fbo':
            self.datas = Fbo.objects.all()
        elif self.data_type == 'fbo_sale':
            self.datas = FboForSale.objects.all()
        elif self.data_type == 'facilities':
            self.datas = Facilities.objects.all()
        elif self.data_type == 'jobsto' or self.data_type == 'jobsfrom' or self.data_type == 'assignment':
            self.datas = Assignment.objects.all()
        elif self.data_type == 'stat':
            self.datas = Stat.objects.all()
        elif self.data_type == 'use':
            self.datas = Use.objects.all()
        elif self.data_type == 'flights':
            self.datas = Flight.objects.all()
        elif self.data_type == 'groupflights':
            self.datas = GroupFlight.objects.all()
        elif self.data_type == 'bank':
            self.datas = Bank.objects.all()

        return self.datas

    def delete_datas(self):
        for data in self.datas:
            data.delete()


# Class time operations
class TimeOperation:
    """
    cet outil permet de transformer les valeurs numériques ou
    horaire en fonction des besoins de l'application
    """

    def __init__(self):
        pass

    def value_hours(self, duration):
        """
        duration is a datetime.time  hh:mm:ss
        :param value: duration
        :return: duration in hours and decimal fraction of hour
        """
        # h, m, s = duration.split(":")
        t = datetime.timedelta(hours=duration.hour, minutes=duration.minute, seconds=duration.second)
        return datetime.timedelta.total_seconds(t) / 3600

    def get_date(self, s_date):
        """
        retourne une date à partir d'une string
        :param: s_date a string
        :return: une date formatée
        """
        return datetime.datetime.strptime(s_date, "AAAA/MM/JJ HH:MM:SS").date()

# TODO en dev
    def get_date_str_to_date(self, s_date):

        if len(s_date) == 19:
            # print(f"bon format d'entrée pour {s_date}")
            y = int(s_date[:4])
            # print('Année' , y, type(y))
            m = int(s_date[5:7])
            # print('Mois', m)
            j = int(s_date[8:10])
            # print('Jour', j)

            dd = datetime.date(y, m, j)
            # print(dd, type(dd))
            return dd

    def get_nb_day_challenge(self):
        start_date = datetime.date(2019, 8, 31)
        today = datetime.date.today()
        date_interval = today - start_date

        return date_interval.days



# def mesurer_temps(nb_secs):
#     """Contrôle le temps mis par une fonction pour s'exécuter.
#     Si le temps d'exécution est supérieur à nb_secs, on affiche une alerte"""
#
#     def decorateur(fonction_a_executer):
#         """Notre décorateur. C'est lui qui est appelé directement LORS
#         DE LA DEFINITION de notre fonction (fonction_a_executer)"""
#
#         def fonction_modifiee(*args, **kwargs):
#             """Fonction renvoyée par notre décorateur. Elle se charge
#             de calculer le temps mis par la fonction à s'exécuter"""
#
#             tps_avant = time.time()  # avant d'exécuter la fonction
#             ret = fonction_a_executer(*args, **kwargs)
#             tps_apres = time.time()
#             tps_execution = tps_apres - tps_avant
#             if tps_execution >= nb_secs:
#                 # print("La fonction {0} a mis {1} pour s'exécuter".format(fonction_a_executer, tps_execution))
#                 print(f"La fonction {fonction_a_executer} a mis {tps_execution} pour s'exécuter")
#             return ret
#
#         return fonction_modifiee
#
#     return decorateur


######################
# Classes management #
######################

# class de gestion des entitées facilities
class ManageFacilities:
    """
    Procédure pour obtenir la liste à jour des facilities de la compagnie
    sous la forme fac1-fac2-fac3
    à partir des tables locales
    C'est un critère utilisé pour aller chercher les données d'assagnment
    des différentes 'facilities'
    """

    def __init__(self):
        self.facilities = Facilities.objects.all()
        self.facilities_icao = self.get_icao_list()
        self.facilities_string = ''
        self.facilities_rent_cost_dict = {}
        self.facilities_monthly_rent_cost_dict = {}
        self.facilities_booking_fee_dict = {}
        self.facilities_pilote_fee_dict = {}
        self.facilities_gcf_dict = {}
        self.facilities_refuelling_dict = {}
        self.cpt = 0

    def update_list(self):

        CleanDBObject('facilities').delete_datas()

        for account in Accounts().get_list_accounts():
            extract_datas_facilities(account)
            time.sleep(2)

    def get_icao_list(self):
        facilities_list = []

        for facility in self.facilities:
            facilities_list.append(facility.icao)

        return facilities_list

    def build_icao_string(self):
        """
        construction du critère pour le query FSE
        :return:
        """
        for elem in self.facilities_icao:
            self.facilities_string += elem + "-"

        return self.facilities_string[0:-1]

    def get_list(self):
        return self.facilities

    def get_built_cost(self, icao):
        try:
            facilitiy = FacilitiesCost.objects.get(icao=icao)
            return facilitiy.builtcost
        except Exception as e:
            print(f"Le FBO {icao} n'est pas enregistré dans la table Facilitieiscost. {str(e.args)}")
            return 0.0

    def get_investissement_total(self):
        total = 0.0

        for fac in self.facilities:
            total += fac.buildcost

        return total

    def get_total_monthly_rent_cost(self):
        rent_cost = self.facilities.aggregate(Sum('monthly_cost'))
        if not rent_cost['monthly_cost__sum']:
            rent_cost['monthly_cost__sum'] = 0

        return rent_cost['monthly_cost__sum']

    def get_monthly_rent_cost_by_icao(self, icao):
        rent_cost = self.facilities.filter(icao=icao).aggregate(Sum('monthly_cost'))
        if not rent_cost['monthly_cost__sum']:
            rent_cost['monthly_cost__sum'] = 0.0

        return rent_cost['monthly_cost__sum']

    def get_monthly_rent_cost_by_icao_dict(self):
        for icao in self.get_icao_list():
            self.facilities_rent_cost_dict[icao] = self.get_monthly_rent_cost_by_icao(icao)

        return self.facilities_monthly_rent_cost_dict

    def get_total_rent_cost(self):
        rent_cost = self.facilities.aggregate(Sum('rentcost'))
        if not rent_cost['rentcost__sum']:
            rent_cost['rentcost__sum'] = 0

        return rent_cost['rentcost__sum']

    def get_rent_cost_by_icao(self, icao):
        rent_cost = self.facilities.filter(icao=icao).aggregate(Sum('rentcost'))
        if not rent_cost['rentcost__sum']:
            rent_cost['rentcost__sum'] = 0.0

        return rent_cost['rentcost__sum']

    def get_rent_cost_by_icao_dict(self):
        for icao in self.get_icao_list():
            self.facilities_rent_cost_dict[icao] = self.get_rent_cost_by_icao(icao)

        return self.facilities_rent_cost_dict

    def get_booking_fee_cost_by_icao(self, account, icao):
        """
        retourne le total des frais de booking payé pour un fbo particulier
        :param icao:
        :return:
        """
        fee = Bank.objects.filter(Q(reason='Booking Fee') &
                                  Q(origine=account) &
                                  Q(location=icao)).aggregate(Sum('amount'))
        if not fee['amount__sum']:
            fee['amount__sum'] = 0.0

        return fee['amount__sum']

    def get_booking_fee_cost_dict(self, account):
        """
        obtenir les couts de booking fee pour toutes les facilities de la compagnie
        :return:
        """
        for icao in self.get_icao_list():
            self.facilities_booking_fee_dict[icao] = self.get_booking_fee_cost_by_icao(account, icao)

        return self.facilities_booking_fee_dict

    def get_gcf_cost_by_icao(self, account, icao):
        """
        obtenir les ground crew fee par icao
        :return:
        """
        gcf = Bank.objects.filter(Q(reason='FBO ground crew fee') &
                                  Q(location=icao) &
                                  Q(origine=account)).aggregate(Sum('amount'))
        if not gcf['amount__sum']:
            gcf['amount__sum'] = 0.0

        return gcf['amount__sum']

    def get_gcf_cost_dict(self, account):
        """
        obtenir les ground crew fee de tous les FBO's de la compagnie
        dans un dictionnaire
        :return:
        """
        for icao in self.get_icao_list():
            self.facilities_gcf_dict[icao] = self.get_gcf_cost_by_icao(account, icao)

        return self.facilities_gcf_dict

    def get_pilot_fee_cost_by_icao(self, account, icao):
        """
        obtenir les pilot fee par icao
        :return:
        """
        pilot_fee = Bank.objects.filter(Q(reason='Pilot Fee') &
                                        Q(location=icao) &
                                        Q(origine=account)).aggregate(Sum('amount'))
        if not pilot_fee['amount__sum']:
            pilot_fee['amount__sum'] = 0.0

        return pilot_fee['amount__sum']

    def get_pilot_fee_cost_dict(self, account):
        """
        obtenir les pilot fee de tous les FBO's de la compagnie
        dans un dictionnaire
        :return:
        """
        for icao in self.get_icao_list():
            self.facilities_pilote_fee_dict[icao] = self.get_pilot_fee_cost_by_icao(account, icao)

        return self.facilities_pilote_fee_dict

    def get_refuel_income_by_icao(self, account, icao):
        """
        obtenir le montant de fuel vendu dans un fbo particulier
        :param icao:
        :return:
        """
        fuel_fee = Bank.objects.filter(Q(reason__contains='Refuelling') &
                                       Q(location=icao)).aggregate(Sum('amount'))
        if not fuel_fee['amount__sum']:
            fuel_fee['amount__sum'] = 0.0

        return fuel_fee['amount__sum']

    def get_refuel_income_dict(self, account):
        """
        obtenir les revenus de fuel pour tous les facilities
        :param account:
        :return:
        """
        for icao in self.get_icao_list():
            self.facilities_refuelling_dict[icao] = self.get_refuel_income_by_icao(account, icao)

        return self.facilities_refuelling_dict

    def get_costs_by_icao(self, icao):
        """
        obtenir le total des coûts pour un facility
        :param icao:
        :return:
        """
        account = "GaugaugAir Texas"
        costs = (self.get_rent_cost_by_icao(icao) +
                 self.get_monthly_rent_cost_by_icao(icao) +
                 self.get_built_cost(icao))

        return costs

    def get_income_by_icao(self, icao):
        """
        obtenir les revenus d'une facility
        :param icao: l'identification de la facility
        :return: le montant de revenu
        """
        account = "GaugauAir Texas"
        incomes = (self.get_booking_fee_cost_by_icao(account, icao) +
                   self.get_gcf_cost_by_icao(account, icao) +
                   self.get_pilot_fee_cost_by_icao(account, icao) +
                   self.get_refuel_income_by_icao(account, icao))
        return incomes

    def get_incomes_total(self):
        income_total = 0.0
        for a in self.facilities_icao:
            income_total += self.get_income_by_icao(a)

        return income_total

    def get_profit_by_icao(self, icao):
        return self.get_income_by_icao(icao) - self.get_costs_by_icao(icao)

    # @mesurer_temps(1)
    def get_profit_total(self):
        profit_total = 0.0
        for a in self.facilities_icao:
            profit_total += self.get_profit_by_icao(a)
        if profit_total == 0:
            return 1
        return profit_total


# class de gestion des fbo's
class ManageFbos:

    def __init__(self):
        self.fbos = Fbo.objects.all().order_by('owner')
        self.list_icao = []
        self.list_account = Accounts().get_list_accounts()
        self.cpt = 0

    def update_list(self):
        """
        mettre à jour la liste des fbos en usage
        et des fbos à vendre
        :return:
        """
        list_account = self.list_account
        CleanDBObject('fbo').delete_datas()

        try:
            for account in list_account:
                extract_datas_fbo(account)
                time.sleep(2)
        except KeyError:
            print(message, 'Fbo update')

            # les fbos à vendre
            print("Les FBO's en vente actuellement ....")
            time.sleep(2)
            self.update_for_sale()

    def get_list(self):
        """
        obtenir la liste des objets FBO
        :param account:
        :return:
        """
        return self.fbos

    def get_list_for_network(self, network_name):
        """
        obtenir la liste des fbos d'un réseau particulier
        :param network_name: le nom du réseau
        :return:
        """
        list_fbo = []
        fbos = Fbo.objects.filter(owner__contains=network_name)
        for el in fbos:
            list_fbo.append(el)

        return list_fbo

    def get_list_icao(self):
        """
        obtenir la liste des identifiants ICAO des FBO's
        :return:
        """
        for fbo in self.get_list():
            self.list_icao.append(fbo.icao)

        return self.list_icao

    def get_rank(self, icao):
        """
        obtenir le rang d'un Fbo en fonction de son icao
        :param icao:
        :return:
        """
        datas = Rank.objects.filter(icao=icao).get()
        return datas

    def get_infos_one_fbo(self, icao):
        """
        obtenir toute l'info d'un fbo particulier en fonction de son icao
        :param icao: l'identifiant du fbo
        :return: un objet Fbo
        """
        datas = Fbo.objects.get(icao=icao)
        return datas

    # les fbo's en vente
    def update_for_sale(self):
        """
        mettre à jour la table locale des fbos en vente
        sur le serveur FSE
        :return:
        """
        CleanDBObject('fbo_sale').delete_datas()
        extract_datas_fbo_sale()

    def get_fbo_for_sale_localisation(self, location):
        """
        obtenir la liste des fbos en vente pour un lieu donné
        à partir de la base de données locale
        :param location:
        :return:
        """
        # CleanDBObject('fbo_sale').delete_datas()
        # extract_datas_fbo_sale()
        fbos = FboForSale.objects.filter(location__contains=location)
        return fbos

    def get_by_num_lot(self, num_lot):
        """
        obtenir la liste des fbo's qui contiennent un nombre de lot
        particulier
        :param num_lot: le nombre de lot recherché
        :return: la liste des fbos correspondants à la recherche
        """
        fbos_lot = FboForSale.objects.filter(lots=num_lot)
        return fbos_lot


# classe de gestion des vols
class ManageFlights:
    """
    Procédure pour obtenir les informations financières des vols
    afin de sortir des ratios de rentabilité
    """

    def __init__(self):
        self.flights = Flight.objects.filter(distance__gt=0).order_by('-time')
        self.cpt = 0

    def get_all(self):
        """
        retourne tous les vols de la compagnie enregistrés dans la table locale
        :return: un queryset contenant tous les vols de tous les avions
        """
        return self.flights

    def get_by_registration(self, registration):
        """
        retourne tous les vols d'un avion particulier
        :param registration:
        :return:
        """
        fs = self.flights.filter(aircraft=registration)
        if fs:
            return fs

    def get_by_ids(self, start, stop):
        """
        retourne les vols compris entre (inclusivement) les ID en paramètre
        :param start:
        :param stop:
        :return:
        """
        flights = self.flights.filter(Q(id__gte=start) & Q(id__lte=stop))
        cpt = 0
        incomes = 0.0
        pilotfee = 0.0
        crewcost = 0.0
        bookingfee = 0.0
        fuelcost = 0.0
        groundcrewfee = 0.0
        rentalcost = 0.0
        profit = 0.0

        results = {}

        for flight in flights:
            cpt += 1
            incomes += flight.income
            pilotfee += flight.pilotfee
            crewcost += flight.crewcost
            bookingfee += flight.bookingfee
            fuelcost += flight.fuelcost
            groundcrewfee += flight.groundcrewfee
            rentalcost += flight.rentalcost

        profit = incomes - (crewcost + bookingfee + groundcrewfee)
        results['incomes'] = incomes
        results['profits'] = profit

        return results

    def get_last_50_by_registration(self, registration):
        """
        retourne les 50 derniers vols d'un avion particulier
        :param registration: l'identification ICAO d'un avion
        :return: un query contenant tous les vols d'un avion
        """
        return self.flights.filter(aircraft=registration)[:50]

    def get_by_registration_by_fbo(self, registration, fbo):
        """
        retourne les vols d'un avion pour un fbo particulier
        :param registration:
        :param fbo:
        :return:
        """
        fl = self.get_by_registration(registration)
        return fl.filter(Q(origine=fbo) | Q(destination=fbo))

    def get_income_by_registration(self, registration):
        """
        les revenus d'un avion particulier
        :param registration:
        :return:
        """
        if self.get_by_registration(registration):
            # spécial challenge
            mydate = None
            if registration == "N652DG":
                mydate = datetime.date(2019, 9, 1)
            elif registration == 'N652DO':
                mydate = datetime.date(2019, 9, 5)
            elif registration == 'N652YL':
                mydate = datetime.date(2019, 9, 8)
            elif registration == 'N968SA':
                mydate = datetime.date(2019, 9, 11)
            elif registration == 'N652AL':
                mydate = datetime.date(2019, 9, 30)

            income = Flight.objects.filter(Q(aircraft=registration) & Q(time__gte=mydate)).aggregate(Sum('income'))
            return income['income__sum']
        else:
            return 0.0

    def get_fees_by_registration(self, registration):
        """
        Retourne le total des frais pour un avion particulier
        :param registration:
        :return:
        """
        if self.get_by_registration(registration):
            # spécial challenge
            mydate = None
            if registration == 'N652DG':
                mydate = datetime.date(2019, 9, 1)
            elif registration == 'N652DO':
                mydate = datetime.date(2019, 9, 5)
            elif registration == 'N652YL':
                mydate = datetime.date(2019, 9, 8)
            elif registration == 'N968SA':
                mydate = datetime.date(2019, 9, 11)
            elif registration == 'N652AL':
                mydate = datetime.date(2019, 9, 30)

            ground_fees = Flight.objects.filter(Q(aircraft=registration) & Q(time__gte=mydate)).aggregate(Sum('groundcrewfee'))
            fuel_fees = Flight.objects.filter(Q(aircraft=registration) & Q(time__gte=mydate)).aggregate(Sum('fuelcost'))
            if ground_fees is None:
                ground_fees = 0
            if fuel_fees is None:
                fuel_fees = 0

            return ground_fees['groundcrewfee__sum'] + fuel_fees['fuelcost__sum']
        else:
            return 0.0

    def get_total_flight_time_by_registration(self, registration):
        total_flight_time = 0
        for elem in self.get_by_registration(registration):
            total_flight_time += TimeOperation().value_hours(elem.flighttime)

        return total_flight_time

    def get_income_by_registration_by_fbo(self, registration, fbo):
        """
        les revenus d'un fbo par un avion particulier
        :param registration:
        :param fbo:
        :return:
        """
        total = 0.0
        fl = self.get_by_registration_by_fbo(registration, fbo)
        for f in fl:
            total += f.income
        return total

    def get_profit_by_registration(self, registration):
        """
        les profits (income - frais) d'un avion particulier
        :param registration:
        :return:
        """
        total = self.get_income_by_registration(registration)
        frais = total * 0.2
        return total - frais

    def get_profit_by_registration_by_fbo(self, registration, fbo):
        """
        les profits (income - frais) d'une avion particulier et FBO particulier
        :param registration:
        :param fbo:
        :return:
        """
        total = self.get_income_by_registration_by_fbo(registration, fbo)
        frais = total * 0.2
        return total - frais

    def update(self, account='domfse', month=None, year=None):
        """
        mettre à jour la table locale à partir du serveur FSE
        :param account: par défaut c'est domfse (le propriétaire de tous les avions)
        :param month: par défaut le mois actuel
        :param year: par défaut l'année actuelle
        """
        aircrafts = ManageAircrafts().get_list_registration()
        for registration in aircrafts:
            extract_datas_flights(registration, account, month, year)
            time.sleep(2)

    # SPECIAL DHALLENGE60DAYS
    def get_challenge_info(self):
        challenge_aircrafts = []

        aircrafts = ManageAircrafts().get_aircrafts_challenge_list()
        for aircraft in aircrafts:
            challenge_aircrafts.append(self.get_challenge_info_by_registration(aircraft.registration))

        return challenge_aircrafts

    def get_total_flight_time_by_registration_challenge(self, registration):
        total_flight_time = 0
        mydate = None

        if registration == 'N652DG':
            mydate = datetime.date(2019, 9 ,1)
        elif registration == 'N652DO':
            mydate = datetime.date(2019, 9, 5)
        elif registration == 'N652YL':
            mydate = datetime.date(2019, 9, 8)
        elif registration == 'N968SA':
            mydate = datetime.date(2019, 9, 11)
        elif registration == 'N652AL':
            mydate = datetime.date(2019, 9, 30)

        vols = self.get_by_registration(registration)
        # print(f"avion : {registration} - nb vols {len(vols)} - date de début : {mydate}")

        for elem in vols.filter(time__gte=mydate):
            total_flight_time += TimeOperation().value_hours(elem.flighttime)
        # print(f"avion : {registration} - hrs de vol : {total_flight_time} hrs")
        return total_flight_time

    def get_total_distance_by_registration_challenge(self, registration):
        total = 0.0
        mydate = None

        if registration == 'N652DG':
            mydate = datetime.date(2019, 9, 1)
        elif registration == 'N652DO':
            mydate = datetime.date(2019, 9, 5)
        elif registration == 'N652YL':
            mydate = datetime.date(2019, 9, 8)
        elif registration == 'N968SA':
            mydate = datetime.date(2019, 9, 11)
        elif registration == 'N652AL':
            mydate = datetime.date(2019, 9, 30)

        vols = self.get_by_registration(registration)
        for elem in vols.filter(time__gte=mydate):
            if elem.distance:
                total += elem.distance

        return total

    # special challenge
    def get_challenge_recap(self):
        recap_income = 0.0
        recap_fees = 0.0
        recap_hours = 0.0
        start = 100000
        former_aircraft = 268200
        actual_aircraft = 281200
        next_aircraft = 563800
        nb_days = TimeOperation().get_nb_day_challenge()

        aircrafts = ManageAircrafts().get_aircrafts_challenge_list()
        for aircraft in aircrafts:
            recap_income += self.get_income_by_registration(aircraft.registration)
            recap_fees += self.get_fees_by_registration(aircraft.registration)
            recap_hours += self.get_total_flight_time_by_registration_challenge(aircraft.registration)

        recap_balance = (recap_income - recap_fees)+ (start - actual_aircraft)
        final_income = recap_balance + actual_aircraft
        objectif = next_aircraft - final_income
        avg_income = (recap_income - recap_fees) / nb_days
        avg_hour = recap_hours / nb_days
        avg_income_by_hour = avg_income / avg_hour


        recap = {'income': recap_income, 'fees': recap_fees, 'balance': recap_balance, 'objectif': objectif,
                 'average_income': avg_income, 'nb_days': nb_days, 'average_hours': avg_hour,
                 'average_income_by_hour': avg_income_by_hour, 'final_bank': final_income,
                 }
        return recap

    # special challenge
    def get_challenge_info_by_registration(self, registration):
        if self.get_by_registration(registration):
            infos = {'aircraft': registration, 'flight_time': self.get_total_flight_time_by_registration_challenge(registration),
                     'distance': self.get_total_distance_by_registration_challenge(registration),
                     'income': self.get_income_by_registration(registration),
                     'fees': self.get_fees_by_registration(registration)}

            return infos
        else:
            return None

    def get_total_distance_by_registration(self, registration):
        total = 0.0
        for elem in self.get_by_registration(registration):
            if elem.distance:
                total += elem.distance

        return total

    def get_total_income_by_registration(self, registration):
        total = 0.0
        for elem in self.get_by_registration(registration):
            if elem.income:
                total += elem.income

        return total

    def get_ratio_by_hour(self, registration):
        """
        obtenir la rentabilité d'un avion particulier
        calcul fait pour une unité HEURE
        :param registration: l'identifiant de l'avion
        :return: la valeur du ratio
        """
        if self.get_total_flight_time_by_registration(registration) == 0:
            ratio = 0
        else:
            ratio = self.get_total_income_by_registration(registration) / self.get_total_flight_time_by_registration(
                registration)

        return ratio

    def get_ratio_by_nm(self, registration):
        """
        obtenir la rentabilité d'un avion particulier
        calcul fait pour un mille nautique
        :param registration: l'identifiant de l'avion
        :return: la valeur du ratio
        """
        if self.get_total_distance_by_registration(registration) == 0:
            ratio = 0
        else:
            ratio = self.get_total_income_by_registration(registration) / self.get_total_distance_by_registration(
                registration)

        return ratio

    def get_ratio_financial(self, registration):
        """
        obtenir le pourcentage de retour sur investissement pour un avion particulier
        :param registration: l'identifiant de l'avion
        :return: la valeur du ratio
        """
        aircraft = Use.objects.get(immat=registration)
        if float(aircraft.lease) > 0:
            return (float(aircraft.profits) / float(aircraft.lease)) * 100
        else:
            return 0

    def get_lease_from(self, registration):
        """
        obtenir le leaser pour un avion particulier
        :param registration: l'identifiant de l'avion
        :return: le leaser
        """
        aircraft = Aircraft.objects.get(registration=registration)
        return aircraft.leasedfrom


# class de gestion des entitées aircrafts
class ManageAircrafts:
    """
    Procédures pour obtenir les informations necessaires au site
    à partir des tables locales.
    """

    def __init__(self):
        self.aircrafts = Aircraft.objects.filter(actif=True)
        self.list_registration = []
        self.list_rental_income = {}
        self.list_assignment_income = {}
        self.list_fuel_cost = {}
        self.list_maintenance_cost = {}
        self.list_lease_cost = {}
        self.list_ownership_cost = {}
        self.list_sale_cost = {}

    def get_aircrafts_list(self):
        """
        retourne la liste des objects aircrafts contenu dans la table avion_aircrafts
        :return:
        """
        return self.aircrafts

    def get_aircrafts_actif_list(self):
        """
        retourne la liste des aircrafts actifs uniquement
        :return:
        """
        return  self.aircrafts.filter(actif=True)

    def get_aircrafts_challenge_list(self):
        """
        retourne la liste des avions engagés dans le challenge 60Days
        :return:
        """
        return self.aircrafts.filter(challenge=True)

    def get_by_registration(self, registration):
        """
        retourne les informations d'un avion particulier
        :param registration:
        :return:
        """
        return self.aircrafts.get(registration=registration)

    def get_use_datas(self):
        return Use.objects.all()

    def get_total_monthly_fee(self):
        mf = Aircraft.objects.filter(leasedfrom__startswith='GaugauAir').aggregate(Sum('monthlyfee'))
        if not mf['monthlyfee__sum']:
            mf['monthlyfee__sum'] = 0.0

        return mf['monthlyfee__sum']

    def get_profit_total(self):
        profit_total = 0.0
        elems = self.get_use_datas()
        for a in elems:
            profit_total += float(a.profits)

        return profit_total

    def get_list_registration(self):
        """
        retourne la liste des immatriculations de la flotte
        :return: une liste
        """
        for aircraft in self.aircrafts:
            self.list_registration.append(aircraft.registration)

        return self.list_registration

    # income #
    def get_external_rental_income_by_registration(self, registration, month=None):
        """
        retourne le montant généré par les locations d'un avion particulier en fonction de son immatriculation
        :param account: le compte qui possède l'avion
        :param registration: l'avion recherché
        :param month: le mois recherché
        :return: un montant (float)
        """
        if month is None:
            rental = Bank.objects.filter(Q(aircraft=registration) &
                                         Q(reason='Rental of aircraft')).exclude(origine='domfse').aggregate(
                Sum("amount"))
        else:
            # TODO 18-12-08 dominiqueIMac: impossible de filtrer sur le mois!
            # TODO 18-12-08 dominiqueIMac: date_item est bien un DateTimeField
            # TODO 18-12-08 dominiqueIMac: mais il ne reconnait pas le mois ni en INT ni en STR
            rental = Bank.objects.filter(Q(aircraft=registration) &
                                         Q(reason='Rental of aircraft') &
                                         Q(date_item__month=str(month))).exclude(origine='domfse').aggregate(
                Sum('amount'))

        if not rental['amount__sum']:
            rental['amount__sum'] = 0.0

        return rental['amount__sum']

    def get_rental_income_by_registration(self, registration):
        """
        retourne le montant généré par les locations d'un avion particulier en fonction de son immatriculation
        :param account:
        :param registration:
        :return: un montant (float)
        """
        # rental = Bank.objects.filter(Q(aircraft=registration) &
        #                              Q(reason='Rental of aircraft') &
        #                              Q(destinataire=account)).aggregate(Sum("amount"))
        rental = Bank.objects.filter(Q(aircraft=registration) &
                                     Q(reason='Rental of aircraft')).aggregate(Sum("amount"))

        if not rental['amount__sum']:
            rental['amount__sum'] = 0.0

        return rental['amount__sum']

    def get_list_rental_income_by_registration(self):
        """
        retourne un dictionnaire avec l'immatriculation et le montant généré par la location
        pour tous les avions de la flotte
        :param account:
        :return: un dictionnaire
        """
        lista = self.get_list_registration()
        for elem in lista:
            self.list_rental_income[elem] = self.get_rental_income_by_registration(elem)

        return self.list_rental_income

    def get_assignment_income_by_registration(self, registration):
        """
        retourne le montant généré par les pax transportés pour un avion particulier
        en fonction de son immatriculation
        :param account:
        :param registration:
        :return: un montant (float)
        """
        assignments = Bank.objects.filter(Q(aircraft=registration) &
                                          Q(reason='Pay for assignment')).aggregate(Sum("amount"))

        if not assignments['amount__sum']:
            assignments['amount__sum'] = 0.0

        return assignments['amount__sum']

    def get_list_assignment_income_by_registration(self):
        """
        retourne un dictionnaire avec l'immatriculation et le montant généré par les pax transportés
        pour tous les avions de la flotte
        :param account:
        :return: un dictionnaire
        """
        lista = self.get_list_registration()
        for elem in lista:
            self.list_assignment_income[elem] = self.get_assignment_income_by_registration(elem)

        return self.list_assignment_income

    # costs #

    def get_fuel_cost_by_registration(self, registration):
        """
        retourne le montant dépensé en fuel pour un avion particulier

        :param account:
        :param registration:
        :return:
        """
        fuel_cost = Bank.objects.filter(Q(aircraft=registration) &
                                        Q(reason__contains='Refuelling')).aggregate(Sum('amount'))

        if not fuel_cost['amount__sum']:
            fuel_cost['amount__sum'] = 0.0

        return fuel_cost['amount__sum']

    def get_list_fuel_cost_by_registration(self):
        """
        retourne un dictionnaire avec l'immatriculation et le montant dépensé en fuel
        pour tous les avions de la flotte
        :param account:
        :return: un dictionnaire
        """
        lista = self.get_list_registration()
        for elem in lista:
            self.list_fuel_cost[elem] = self.get_fuel_cost_by_registration(elem)

        return self.list_fuel_cost

    def get_maintenance_cost_by_registration(self, registration):
        """
        retourne le montant dépensé en fuel pour un avion particulier
        note : Pour le moment Sapper est le destinataire utilisé. À la fin du
        remboursement le destinataire sera modifié pour GaugauAir
        :param account:
        :param registration:
        :return:
        """
        # maintenance_cost = Bank.objects.filter(Q(aircraft=registration) &
        #                                 Q(reason__contains='Aircraft maintenance') &
        #                                 Q(origine__contains=account)).aggregate(Sum('amount'))
        maintenance_cost = Bank.objects.filter(Q(aircraft=registration) &
                                               Q(reason__contains='Aircraft maintenance')).aggregate(Sum('amount'))

        if not maintenance_cost['amount__sum']:
            maintenance_cost['amount__sum'] = 0.0

        return maintenance_cost['amount__sum']

    def get_list_maintenance_cost_by_registration(self):
        """
        retourne un dictionnaire avec l'immatriculation et le montant dépensé en fuel
        pour tous les avions de la flotte
        :param account:
        :return: un dictionnaire
        """
        lista = self.get_list_registration()
        for elem in lista:
            self.list_maintenance_cost[elem] = self.get_maintenance_cost_by_registration(elem)

        return self.list_maintenance_cost

    def get_lease_cost_by_registration(self, registration):
        """
        retourne le montant dépensé en leasing pour un avion particulier
        :param account:
        :param registration:
        :return:
        """
        lease_cost = Bank.objects.filter(Q(reason='Group payment') &
                                         Q(comment__contains=registration)).aggregate(Sum('amount'))

        if not lease_cost['amount__sum']:
            lease_cost['amount__sum'] = 0.0

        # erreur de saisie dans le system de banque
        if registration == 'VH-MDP':
            lease_cost['amount__sum'] -= 250000

        return lease_cost['amount__sum']

    def get_list_lease_cost_by_registration(self):
        """
        retourne un dictionnaire avec l'immatriculation et le montant dépensé en fuel
        pour tous les avions de la flotte
        :param account:
        :return: un dictionnaire
        """
        lista = self.get_list_registration()
        for elem in lista:
            self.list_lease_cost[elem] = self.get_lease_cost_by_registration(elem)

        return self.list_lease_cost

    def get_ownership_cost_by_registration(self, registration):
        """
        retourne le montant dépensé en monthly fee pour un avion particulier
        :param account:
        :param registration:
        :return:
        """
        ownership_cost = Bank.objects.filter(Q(aircraft=registration) &
                                             Q(reason__contains='Ownership Fee')).aggregate(Sum('amount'))

        if not ownership_cost['amount__sum']:
            ownership_cost['amount__sum'] = 0.0

        return ownership_cost['amount__sum']

    def get_list_ownership_cost_by_registration(self):
        """
        retourne un dictionnaire avec l'immatriculation et le montant dépensé en monthly fee
        pour tous les avions de la flotte
        :param account:
        :return: un dictionnaire
        """
        lista = self.get_list_registration()
        for elem in lista:
            self.list_ownership_cost[elem] = self.get_ownership_cost_by_registration(elem)

        return self.list_ownership_cost

    def update_list(self):
        """
        mettre à jour la liste des avions en usage
        :return:
        """
        extract_datas_aircraft()
        print('Aircrafts list update done')

    def update_aircrafts_use_datas(self):
        """
        calculs pour chacun des avions contenus dans le dict aircrafts
        :param avions:
        :return:
        """
        CleanDBObject('use').delete_datas()
        aircrafts = ManageAircrafts().get_aircrafts_list()

        # TODO 18-11-03 dominiqueIMac: Modifier la procédure pour qu'elle soit multicompte par défaut
        # account = 'domfse'

        # calculer les dernières valeurs pour chaque avion
        # et les enregistrer dans avion_usage (mise à jour)
        for aircraft in aircrafts:
            # serialnumber and registration
            registration = aircraft.registration
            serialnumber = aircraft.serialnumber

            # rental income
            rental_income = ManageAircrafts().get_external_rental_income_by_registration(registration)

            # assignment income
            assignment_income = ManageAircrafts().get_assignment_income_by_registration(registration)

            # ownerfee
            ownerfee_cost = ManageAircrafts().get_ownership_cost_by_registration(registration)

            # maintenance cost
            maintenance_cost = ManageAircrafts().get_maintenance_cost_by_registration(registration)

            # fuel cost
            fuel_cost = ManageAircrafts().get_fuel_cost_by_registration(registration)

            # lease_cost
            lease_cost = ManageAircrafts().get_lease_cost_by_registration(registration)

            # TODO 18-11-03 dominiqueIMac: trouver les coûts d'achat directement dans les données banquaires
            # condition spéciale pour l'initialisation des données de banque pour deux avions de la flotte
            # if registration == 'N208TH':
            #     lease += 25000
            # if registration == 'N867EX':
            #     lease -= 11333.30
            if registration == 'N652DO':
                lease_cost = 175442
            elif registration == 'N652PT':
                lease_cost = 706548
            elif registration == 'N652GU':
                lease_cost = 721679
            elif registration == 'N652CA':
                lease_cost = 687669
            elif registration == 'N652MI':
                lease_cost = 1120474
            elif registration == 'N652CL':
                lease_cost = 648999
            elif registration == 'N-060EE':
                lease_cost = 150000
            elif registration == 'N208CE':
                lease_cost = 20000
            elif registration == 'N652DA':
                lease_cost = 995439
            elif registration == 'N652MA':
                lease_cost = 571866
            elif registration == 'N652YU':
                lease_cost = 1100000

            profit = (rental_income + assignment_income) - (maintenance_cost + fuel_cost + lease_cost + ownerfee_cost)
            ratio_nm = ManageFlights().get_ratio_by_nm(registration)
            Use.objects.create(
                date_created=timezone.now(),
                serialnumber=serialnumber,
                immat=registration,
                type=aircraft.makemodel,
                gain_location=rental_income,
                gain_travail=assignment_income,
                frais_entretien=maintenance_cost,
                frais_carburant=fuel_cost,
                lease=lease_cost,
                frais_mensuel=ownerfee_cost,
                profits=profit,
                ratio_nm=ratio_nm,
            )
            print('update done for', registration)
        print('Aircrafts update done')

    def change_registration(self, registration, new_registration):
        """
        Modifier l'immat d'un avion particulier
        :param registration: l'immat actuelle
        :param new_registration: la nouvelle immat
        :return: NIL
        """
        self.change_registration_aircraft(registration, new_registration)
        self.change_registration_bank(registration, new_registration)
        self.change_registration_use(registration, new_registration)
        self.change_registration_flight(registration, new_registration)
        self.change_registration_groupflight(registration, new_registration)

    def change_registration_aircraft(self, registration, new_registration):
        """
        Modifier l'immat d'un avion particulier
        :param registration: l'immat actuelle
        :param new_registration: la nouvelle immat
        :return: NIL
        """
        aircraft = Aircraft.objects.get(registration=registration)
        aircraft.registration = new_registration
        aircraft.save()

    def change_registration_bank(self, registration, new_registration):
        """
        modifie la table bank en remplaçant les registrations
        :param registration: l'immat actuelle dans la table
        :param new_registration: la nouvelle immat dans la table
        :return:
        """
        enr = Bank.objects.filter(aircraft=registration)
        for elem in enr:
            elem.aircraft = new_registration
            elem.save()

    def change_registration_use(self, registration, new_registration):
        """
        modifie la table use en remplaçant les registrations
        :param registration: l'immat actuelle dans la table
        :param new_registration: la nouvelle immat dans la table
        :return:
        """
        ac = Use.objects.get(immat=registration)
        ac.immat = new_registration
        ac.save()

    def change_registration_flight(self, registration, new_registration):
        """
        modifie la table avion_flight
        :param registration:
        :param new_registration:
        :return:
        """
        acs = Flight.objects.filter(aircraft=registration)
        for ac in acs:
            ac.aircraft = new_registration
            ac.save()

    def change_registration_groupflight(self, registration, new_registration):
        """
        modifie la table network_groupflight
        :param registration:
        :param new_registration:
        :return:
        """
        acs = GroupFlight.objects.filter(aircraft=registration)
        for ac in acs:
            ac.aircraft = new_registration
            ac.save()


# class de gestion des données bank
class ManageBank:
    """
    Procédure de gestion des données banquaires à partir des tables locales
    """

    def __init__(self, account=None, month=None, year=None):
        self.banks = Bank.objects.all()
        self.accounts = Accounts().get_list_accounts()
        self.results_per_registration = {}
        self.cpt = 0

        if not month:
            self.month = timezone.now().month
        else:
            self.month = month
        if not year:
            self.year = timezone.now().year
        else:
            self.year = year
        self.bank = 0.0
        if not account:
            self.account = 'domfse'
        else:
            self.account = account

    def update(self):
        for account in self.accounts:
            try:
                extract_datas_bank(account, self.month, self.year)
                time.sleep(2)
            except KeyError:
                print(message, ' - bank', account)

    def get_nb_bank_transactions_total(self):
        return len(self.banks)

    def get_nb_bank_transactions_by_account(self):
        pass

    def get_bank_for_registration(self, registration):
        """
        obtenir le montant que rapporte un avion particulier (en fonction
        de son immatriculation)
        :return: un floatk
        """
        total = self.banks.filter(Q(aircraft=registration) &
                                  Q(destinataire=self.account)).aggregate(Sum('amount'))
        if not total['amount__sum']:
            self.bank = 0.0
        else:
            self.bank = float(total['amount__sum'])

        return self.bank

    def get_bank_for_registrations(self):
        """
        obtenir un dictionnaire de tous les avions (immatriculation) et de la
        somme produite par leur travail.
        :return: un dictionnaire contenant une immatriculation et son résultat
        financier.
        """
        list_registrations = ManageAircrafts().get_list_registration()
        for elem in list_registrations:
            self.results_per_registration[elem] = self.get_bank_for_registration(elem)

        return self.results_per_registration

    # @mesurer_temps(1)
    def get_last_date(self):
        return timezone.now()
    #     last_date = Bank.objects.all().aggregate(Max('date_item'))
    #
    #     return last_date['date_item__max']


# class de gestion des données stat
class ManageStats:
    """
    Procédure pour préparer les données de stat en vue de l'affichage sur le site
    """

    def __init__(self, delay=10, month=None):
        self.stats = Stat.objects.all()
        self.month = month
        self.delay = delay
        self.cpt = 0
    #

    # @mesurer_temps(1)
    def get_list(self):
        return self.stats

    def update(self):
        # retrouver tous les comptes actifs de la compagnie
        list_accounts = Accounts().get_list_accounts()

        # nettoyer la table pour avoir uniquement les dernières données à jour
        CleanDBObject('stat').delete_datas()

        # extraire les données du site FSE pour chacun des accounts
        for account in list_accounts:
            try:
                extract_datas_stat(account, self.month)
                time.sleep(2)
            except KeyError:
                print('Pas de donnée (Stats) pour le compte', account)

    def get_profit_total(self):
        return ManageAircrafts().get_profit_total()

    # @mesurer_temps(1)
    def get_cash_amount(self):
        """
        retourne le montant de cash disponible (bank + accounts)
        :return:
        """
        total = 0.0

        for elem in self.stats:
            total += float(elem.bank_balance) + float(elem.personnal_balance)

        return total


# class de gestion des jobs autre que GaugauAir ou domfse

# TODO optimiser le code pour les différents joueurs externes
class ManageJobs:
    def __init__(self):
        self.dva_jobs = Bank.objects.filter(origine__contains='DVA')
        self.oac_jobs = Bank.objects.filter(origine__contains='Outback Air Charter International')
        self.date_debut, self.date_fin, self.week_num = self.get_week_datas()

    def get_oac_jobs(self):
        total = 0.0

        if self.oac_jobs:
            for job in self.oac_jobs:
                total += float(job.amount)

        else:
            total = 0.0
        return total

    def get_dva_jobs(self):
        total = 0.0

        if self.dva_jobs:
            for job in self.dva_jobs:
                total += float(job.amount)
        else:
            total = 0.0
        return total

    def update_dva_week(self):
        print("Update_dva_week")

        if datetime.date.today() < self.date_fin + datetime.timedelta(days=1):
            print(f"la semaine qui commence le {self.date_debut} est en cours. Pas d'enregistrement")
            return

        a = DvaWeek(
            date_from=self.date_debut,
            date_to=self.date_fin,
            week_num=self.week_num + 1,
            ident_actif=self.get_ident_semaine(self.date_debut),
            amount=self.get_dva_jobs_week_current(self.date_debut, self.date_fin)
        )
        a.save()

    def get_dva_jobs_week_current(self, date_debut=None, date_fin=None):
        total = 0.0
        if date_debut is None:
            date_debut = self.date_debut

        if date_fin is None:
            date_fin = self.date_fin

        if self.dva_jobs:
            weekjobs = self.dva_jobs.filter(date_item__range=(date_debut, date_fin))
            if weekjobs:
                for job in weekjobs:
                    total += float(job.amount)
            print(f'Le total de semaine dva est {total}$')
        else:
            total = 0.0
            print(f"la semaaine n'est pas commencée!!!")
        return total

    def get_week_datas(self):
        entries = DvaWeek.objects.all().order_by('-date_to').first()
        date_debut = entries.date_to + datetime.timedelta(days=1)
        date_fin = date_debut + datetime.timedelta(days=6)
        week_num = entries.week_num
        return date_debut, date_fin, week_num

    def get_ident_semaine(self, date_debut):
        """
        retourne l'ident du premier jour de la semaine qui a des vols
        si le premier jour n'est pas volé, alors l'ident du suivant
        un max de 30 est installé pour éviter les boucles infinies.
        :param date_debut:
        :return:
        """
        cpt = 0
        enr = Bank.objects.filter(date_item=date_debut).order_by('-ident').first()
        if enr:
            return enr.ident
        else:
            cpt += 1
            if cpt == 30:
                return
            return self.get_ident_semaine(date_debut + datetime.timedelta(days=1))


# class de gestion des assignments
class ManageAssignments:

    def __init__(self):
        self.assignments = Assignment.objects.filter(commodity__contains='GaugauAir')

    def update(self):
        """
        mettre à jour la table locale des assignment
        pour le moment les FROM uniquement
        :return:
        """
        # nettoyer la table pour avoir uniquement les dernières données à jour
        CleanDBObject('jobsfrom').delete_datas()

        # extraire les données du site FSE pour chacun des groupes NML
        print("")
        print("Départ de la procédure pour les groupes NML")
        for group in Accounts().get_list_account_name_nml():
            try:
                extract_datas_assignment_group(group)
                time.sleep(2)
            except KeyError:
                print(f"Pas de pax pour le groupe {group}")

        # extraire les données du site FSE pour chanun des groupes non-nml
        print("")
        print("Départ de la procédure pour les groupes non-NML")
        for group in Accounts().get_list_account_name_no_nml():
            try:
                list_icao = self.get_list_icao_group(group)
                extract_datas_assignment_from(group, list_icao)
                time.sleep(2)
            except KeyError:
                print(f"probleme de ICAO pour le groupe : {group}")

    def get_list_icao_group(self, group_name):
        """
        counstruit le critére de filtre pour trouver les assignments from
        :param group_name:
        :return:
        """
        str_fbo_group = ""
        for elem in ManageFbos().get_list_for_network(group_name):
            str_fbo_group += elem.icao + "-"

        return str_fbo_group[0:-1]

    def get_list(self, icao):
        """
        obtenir la liste des assignements d'une facilitie identifiée par son icao
        :param icao:
        :return:
        """
        return self.assignments

    def get_income_by_icao(self, icao):
        """
        retourne le montant des assignements d'un FBO particulier (ICAO)
        :param icao:
        :return:
        """
        incomes = Assignment.objects.filter(Q(commodity__contains='GaugauAir') & Q(location=icao)).aggregate(Sum('pay'))
        if incomes['pay__sum']:
            return incomes['pay__sum']
        else:
            return None


############################
# Classes extraction datas #
############################

def extract_datas_stat(account, month=None):
    """
    Données récapitulatives de la compagnie
    pour chacun des comptes actifs.
    Aucun historique, uniquement les données les plus recentes.
    """
    try:
        # extraire les données de FSE pour tous les comptes actifs
        datas = ExtractionDatas('stat', account, month).get_datas()
        if datas:
            a, created = Stat.objects.get_or_create(
                account=datas['@account'],
                personnal_balance=datas['Personal_balance'],
                bank_balance=datas['Bank_balance'],
                flights=datas['flights'],
                total_miles=datas['Total_Miles'],
                time_flown=datas['Time_Flown'],
                date_created=timezone.now()
            )
            if created:
                a.save()

        print('Stats update done for account ', account)
    except KeyError:
        print(message, 'statistique', account)


def extract_datas_facilities(account):
    """
    Appeler la procédure des facilities pour chacun des
    comptes actifs de la compagnie.
    Les données sont extraites du site FSE et placées
    dans la table locale avion_facilities

    """
    try:
        # extraire les données du site FSE pour tous les comptes actifs
        datas = ExtractionDatas('facilities', account).get_datas()

        # le cas où plusieurs éléments facilities sont retournées
        if type(datas) is list:
            # combien de données
            nb = int(len(datas))
            print("facilities number for ", account, nb)

            # remplir la table locale
            for facility in datas:
                a, created = Facilities.objects.get_or_create(
                    icao=facility['Icao'],
                    location=facility['Location'],
                    carrier=facility['Carrier'],
                    commoditynames=facility['CommodityNames'],
                    gatestotal=facility['GatesTotal'],
                    gatesrented=facility['GatesRented'],
                    jobspublic=facility['JobsPublic'],
                    destinations=facility['Destinations'],
                    fbo=facility['Fbo'],
                    status=facility['Status'],
                )
                if created:
                    # calcul cost
                    costs = 0.0
                    # entries = Bank.objects.filter(Q(reason='Facility rent') & Q(location=a.icao))
                    # # le rentcost de chaque FBO
                    # for entry in entries:
                    #     costs += entry.amount
                    a.rentcost = costs
                    # le buildcost individuel (cas par cas)
                    a.buildcost = ManageFacilities().get_built_cost(a.icao)
                    # calcul incomes
                    a.incomes = ManageFacilities().get_income_by_icao(a.icao)
                    a.profits = ManageFacilities().get_income_by_icao(a.icao) - ManageFacilities().get_costs_by_icao(
                        a.icao)
                    a.save()
        # le cas où un seul élément facility est retourné
        if type(datas) is dict:
            facility = datas.values()
            a, created = Facilities.objects.get_or_create(
                icao=facility['Icao'],
                location=facility['Location'],
                carrier=facility['Carrier'],
                commoditynames=facility['CommodityNames'],
                gatestotal=facility['GatesTotal'],
                gatesrented=facility['GatesRented'],
                jobspublic=facility['JobsPublic'],
                destinations=facility['Destinations'],
                fbo=facility['Fbo'],
                status=facility['Status'],
            )
            if created:
                cost = 0.0
                # fbos = Bank.objects.filter(Q(reason='Facility rent') & Q(location=a.icao))
                # # le rentcost de chaque FBO
                # for fbo in fbos:
                #     cost += fbo.amount
                a.rentcost = cost
                # le buildcost individuel (cas par cas)
                if a.icao in ['TA65', '89TS', '77XS']:
                    a.buildcost = 95000
                elif a.rentcost == 0:
                    a.buildcost = 130000
                # TODO 18-11-03 dominiqueIMac: prévoir le cas de location de porte sur FBO
                # le monthly_cost
                a.incomes = ManageFacilities().get_income_by_icao(a.icao)
                a.profits = ManageFacilities().get_income_by_icao(a.icao) - ManageFacilities().get_costs_by_icao(a.icao)
                a.save()

    except KeyError:
        print(message, 'Facility', account)


def extract_datas_bank(account=None, month=None, year=None):
    """
    Extraire les données des mouvements banquaires.

    :return:
    """
    # transformer les données pour les placer dans la bd
    try:
        datas = ExtractionDatas('bank', account, month, year).get_datas()

        if type(datas) is list:
            # combien de données
            nb = int(len(datas))
            print("bank", account, nb)

            # pour chaque payment il faut l'enregistrer dans la bd
            for dico in datas:
                try:
                    b, created = Bank.objects.get_or_create(
                        ident=dico["Id"],
                        destinataire=dico["To"],
                        origine=dico["From"],
                        amount=float(dico["Amount"]),
                        reason=dico["Reason"],
                        fbo=dico["Fbo"],
                        location=dico["Location"],
                        aircraft=dico["Aircraft"],
                        comment=dico["Comment"],
                    )
                    if created:
                        b.date_item = TimeOperation().get_date_str_to_date(dico['Date'])
                        b.save()
                except Exception as e:
                    print(str(e.args))

    except KeyError as e:
        print('Pas de données (bank) pour le compte', account, str(e))


def extract_datas_flights(registration, account='domfse', month=None, year=None):
    """
    Extraire les datas des vols effectués dans FSE
    """
    try:
        # extraire les données du site FSE pour tous les vols enregistrés
        datas = ExtractionDatas('flights', account, month, year, registration).get_datas()

        if type(datas) is list:
            # combien de données
            nb = int(len(datas))
            print("flights", registration, nb)

            # construire la table locale
            for flight in datas:
                a, created = Flight.objects.get_or_create(
                    type=flight['Type'],
                    time=TimeOperation().get_date_str_to_date(flight['Time']),
                    distance=flight['Distance'],
                    aircraft=flight['Aircraft'],
                    makemodel=flight['MakeModel'],
                    origine=flight['From'],
                    destination=flight['To'],
                    flighttime=flight['FlightTime'],
                    income=flight['Income'],
                    pilotfee=flight['PilotFee'],
                    crewcost=flight['CrewCost'],
                    bookingfee=flight['BookingFee'],
                    fuelcost=flight['FuelCost'],
                    groundcrewfee=flight['GCF'],
                    rentalcost=flight['RentalCost'],
                )
                if created:
                    a.save()
        # else:
        #     print('pas de données de vol pour', registration)

        elif type(datas) is dict:
            # combien de données
            nb = int(len(datas))
            print("flights", registration, nb)

            # construire la table locale
            # flight = datas.values()
            # a, created = Flight.objects.get_or_create(
            #     type=flight['Type'],
            #     time=flight['Time'],
            #     distance=flight['Distance'],
            #     aircraft=flight['Aircraft'],
            #     makemodel=flight['MakeModel'],
            #     origine=flight['From'],
            #     destination=flight['To'],
            #     flighttime=flight['FlightTime'],
            #     income=flight['Income'],
            #     pilotfee=flight['PilotFee'],
            #     crewcost=flight['CrewCost'],
            #     bookingfee=flight['BookingFee'],
            #     fuelcost=flight['FuelCost'],
            #     groundcrewfee=flight['GCF'],
            #     rentalcost=flight['RentalCost'],
            # )
            # if created:
            #     # ne conserver que les vols proprement dit
            #     # if a.type == 'flight':
            #     a.save()

        else:
            print('pas de données de vol pour', registration)

    except KeyError:
        print(message, '- flights :', registration)

# def extract_datas_fbo_monthly_summary(account, icao):
#     """
#     extraire les données financières mensuelles d'un FBO
#     :param account: la clef du groupe a qui appatient le fbo
#     :param icao: l'icao du FBO
#     :return:
#     """
#     try:
#         datas = ExtractionDatas('fbo_monthly_summary', account, icao).get_datas()
#
#         if datas:
#             nb = int(len(datas))
#             print()

def extract_datas_fbo(account):
    """
    Extraire les datas des FBO's

    :rtype: object
    :return:
    """
    try:
        # extraire les données du site FSE pour un compte actifs
        datas = ExtractionDatas('fbo', account).get_datas()

        if datas:
            # combien de données
            nb = int(len(datas))
            print("fbo", account, nb)

            # construire la table locale
            for fbo in datas:
                a, created = Fbo.objects.get_or_create(
                    fboid=fbo['FboId'],
                    status=fbo['Status'],
                    airport=fbo['Airport'],
                    owner=fbo['Owner'],
                    icao=fbo['Icao'],
                    location=fbo['Location'],
                    lots=fbo['Lots'],
                    repairshop=fbo['RepairShop'],
                    gates=fbo['Gates'],
                    gatesrented=fbo['GatesRented'],
                    fuel100ll=fbo['Fuel100LL'],
                    fueljeta=fbo['FuelJetA'],
                    buildingmaterials=fbo['BuildingMaterials'],
                    supplies=fbo['Supplies'],
                    suppliesperday=fbo['SuppliesPerDay'],
                    suppliedday=fbo['SuppliedDays'],
                    sellprice=fbo['SellPrice'],
                )
                if created:
                    a.save()
    except KeyError:
        print(message, ' - fligh :', account)


def extract_datas_fbo_sale():
    """
    Extraire les datas des FBO's en vente sur le serveur FSE

    :return:
    """
    try:
        # extraire les données du site FSE pour un compte actifs
        datas = ExtractionDatas('fbo_sale').get_datas()

        if datas:
            # combien de données
            nb = int(len(datas))
            print("fbo_sale", nb)

            # construire la table locale
            for fbo in datas:
                a, created = FboForSale.objects.get_or_create(
                    fboid=fbo['FboId'],
                    status=fbo['Status'],
                    airport=fbo['Airport'],
                    owner=fbo['Owner'],
                    icao=fbo['Icao'],
                    location=fbo['Location'],
                    lots=fbo['Lots'],
                    repairshop=fbo['RepairShop'],
                    gates=fbo['Gates'],
                    gatesrented=fbo['GatesRented'],
                    fuel100ll=fbo['Fuel100LL'],
                    fueljeta=fbo['FuelJetA'],
                    buildingmaterials=fbo['BuildingMaterials'],
                    supplies=fbo['Supplies'],
                    suppliesperday=fbo['SuppliesPerDay'],
                    suppliedday=fbo['SuppliedDays'],
                    sellprice=fbo['SellPrice'],
                )
                if created:
                    a.save()
    except KeyError:
        print(message, ' - fligh :')


def extract_datas_fbo_month(account, icao, month=None, year=None):
    """
    Extraire les datas bilan financier mensuel à partir du server FSE
    :param month: le mois courant si pas de paramètre
    :param year:  l'année courante si pas de paramètre
    :return: NIL
    """

    datas = ExtractionDatas(data_type='fbo_month', account=account, month=month, year=year, registration=None,
                            icao=icao).get_datas()
    # print(type(datas))

    try:
        if datas:
            # nb = int(len(datas))
            # print("fbo mensuel", account, nb)
            for fbo in datas:
                a, created = FboMonth.objects.get_or_create(
                    owner=fbo['Owner'],
                    icao=fbo['ICAO'],
                    month=fbo['Month'],
                    year=fbo['Year'],
                    net_total=fbo['Net_Total'],
                    current_ops=fbo['Current_Ops'],
                )
                if created:
                    a.save()
        else:
            print('Pas de données pour ' + icao)

    except KeyError:
        print(message, ' - fbo mensual :', account)


def extract_datas_assignment_group(group_name):
    """
    extraire les assignments de chaque groupe
    :return:
    """
    datas = ExtractionDatas('group_assignments', group_name).get_datas()
    icao = ""
    try:
        if datas:
            print(f"Nombre d'assignment pour {group_name} : {len(datas)}")
            for assignment in datas:
                icao = assignment['Location']
                a, created = Assignment.objects.get_or_create(
                    ident=assignment['Id'],
                    location=assignment['Location'],
                    toicao=assignment['Destination'],
                    fromicao=assignment['From'],
                    commodity=assignment['Assignment'],
                    unittype=assignment['Units'],
                    amount=assignment['Amount'],
                    pay=assignment['Pay']
                )
                if created:
                    a.save()
        else:
            print(f"Pas de données pour {group_name}")

    except Exception as e:
        print(f"{message} - Assignments ({icao}) - {str(e.args)}")


def extract_datas_assignment_to():
    """
    extraire les données d'assignement (facility) du site fse

    :return:
    """
    try:
        datas = ExtractionDatas('jobsto').get_datas()

        if datas:
            # combien de données
            nb = int(len(datas))
            print("to", nb)

            for assignment in datas:
                a, created = Assignment.objects.get_or_create(
                    ident=assignment['Id'],
                    location=assignment['Location'],
                    toicao=assignment['ToIcao'],
                    fromicao=assignment['FromIcao'],
                    amount=assignment['Amount'],
                    unittype=assignment['UnitType'],
                    commodity=assignment['Commodity'],
                    pay=assignment['Pay']
                )
                if created:
                    a.save()
    except KeyError:
        raise KeyError


def extract_datas_assignment_from(group, list_icao):
    """
    extraire les données d'assignement (facility) du site fse

    :return:
    """
    try:
        datas = ExtractionDatas(data_type='jobsfrom', account=group, icao=list_icao).get_datas()

        if datas:
            # combien de données
            nb = int(len(datas))
            print(f"Nombre d'assignements pour {group} : {nb}")

            for assignment in datas:
                a, created = Assignment.objects.get_or_create(
                    ident=assignment['Id'],
                    location=assignment['Location'],
                    toicao=assignment['ToIcao'],
                    fromicao=assignment['FromIcao'],
                    amount=assignment['Amount'],
                    unittype=assignment['UnitType'],
                    commodity=assignment['Commodity'],
                    pay=assignment['Pay']
                )
                if created:
                    a.save()
    except KeyError:
        raise KeyError


# TODO 18-11-03 dominiqueIMac: et si les avions appartiennent à plusieurs comptes différents
def extract_datas_aircraft():
    """
    nourrir la répartition par avion

    :return:
    """

    # vider la db pour mettre à jour les infos de chaque avion
    CleanDBObject('aircrafts').delete_datas()

    try:
        # récupérer les données
        datas = ExtractionDatas('aircrafts').get_datas()

        if datas:
            # combien de données
            nb = int(len(datas))
            print("aircrafts in use ", nb)

            for avion in datas:
                a, created = Aircraft.objects.get_or_create(
                    serialnumber=avion['SerialNumber'],
                    makemodel=avion['MakeModel'],
                    registration=avion['Registration'],
                    owner=avion['Owner'],
                    location=avion['Location'],
                    location_name=avion['LocationName'],
                    home=avion['Home'],
                    equipment=avion['Equipment'],
                    rental_dry=avion['RentalDry'],
                    rental_wet=avion['RentalWet'],
                    bonus=avion['Bonus'],
                    need_repair=avion['NeedsRepair'],
                    airframe_time=avion['AirframeTime'],
                    engine_time=avion['EngineTime'],
                    last100=avion['TimeLast100hr'],
                    leasedfrom=avion['LeasedFrom'],
                    monthlyfee=avion['MonthlyFee'],
                    feeowed=avion['FeeOwed'],
                )
                if created:
                    if a.leasedfrom == 'NA':
                        a.leasedfrom = 'GaugauAir Aviation'
                    a.save()
            print('Aircrafts update done')

    except KeyError:
        print(message, ' - aircrafts ')
