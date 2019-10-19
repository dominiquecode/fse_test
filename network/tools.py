# les outils de suivi des networks
# dans le cadre des Network Manager Labs

from avion.tools import *
from .models import GroupFlight, Network, Pilot
from avion.models import Bank, Assignment
import time
from django.db.models import Sum, Q, Max, Min


# CLASSES UTILITAIRES #
message = "Problème de connexion avec le serveur FSE "


def extract_datas_network(account):
    """
    retrouve les données bancaires d'un network particulier
    :param account: le nom complet du network
    :return:
    """
    pass


# TODO vérifier la mécanique des champs Time et DateTime
def extract_datas_group_flights(group=None, month=None, year=None):
    """
    Extraire les données des vols effectués pour chacun des groupes de la compagnie
    :param group: le nom du groupe
    :param month: le mois courant par défaut
    :param year: l'année courante par défaut
    :return: None
    """
    try:
        # extraire les données de FSE dans la table locale
        datas = ExtractionDatas('network', group, month, year).get_datas()
        if datas:
            nb = int(len(datas))
            print("group-flights", group, nb)

            for flight in datas:
                try:
                    a, created = GroupFlight.objects.get_or_create(
                        idflight=flight['Id'],
                        type=flight['Type'],
                        # time=flight['Time'],
                        distance=flight['Distance'],
                        pilot=flight['Pilot'],
                        serialnumber=flight['SerialNumber'],
                        aircraft=flight['Aircraft'],
                        makemodel=flight['MakeModel'],
                        origine=flight['From'],
                        destination=flight['To'],
                        # totalenginetime=flight['TotalEngineTime'],
                        # flighttime=flight['FlightTime'],
                        groupname=flight['GroupName'],
                        income=flight['Income'],
                        pilotfee=flight['PilotFee'],
                        crewcost=flight['CrewCost'],
                        bookingfee=flight['BookingFee'],
                        bonus=flight['Bonus'],
                        fuelcost=flight['FuelCost'],
                        gcf=flight['GCF'],
                        rentalprice=flight['RentalPrice'],
                    )
                    if created:
                        a.time = TimeOperation().get_date_str_to_date(flight['Time'])
                        groupincome = float(a.income) - (float(a.pilotfee) + float(a.crewcost) + float(a.bookingfee) +
                                                         float(a.fuelcost) + float(a.gcf) + float(a.rentalprice))
                        a.groupfee=groupincome

                        if float(a.income) != 0.0:
                            pourcentage_group = (float(a.groupfee) / float(a.income)) * 100
                            a.repartition_group = pourcentage_group
                        a.save()

                except Exception as e:
                    print(f"Erreur extraction {group} (str({e.args}))")

    except KeyError:
        print(message, '- Group-flights :', group)


# classe de gestion des groupes de la compagnie
class ManageGroup:

    def __init__(self):
        self.group_list = self._get_group_list()
        self.assignments = Assignment.objects.filter(commodity__contains='GaugauAir')
        self.group_transferts = {}

    def _get_group_list(self):
        """
        retourne la liste de tous les groupes de la compagnie
        :return:
        """
        return Accounts().get_list_account_name()

    def get_fbos_for_network(self, network_name):
        """
        obtenir la liste des objets fbos d'un réseau particulier
        :param network_name: le nom du réseau
        :return:
        """
        list_fbo = []
        fbos = Fbo.objects.filter(owner__contains=network_name)
        for fbo in fbos:
            list_fbo.append(fbo)

        return list_fbo

    def get_nbjobs_from_per_icao(self, icao):
        """
        retourne le nombre de pax actuel d'un fbo particulier
        :param network_name: le nom du network
        :return:
        """
        nb_job = 0
        assignments = self.assignments.filter(fromicao=icao)

        for job in assignments:
            nb_job += job.amount
        return nb_job
        # return assignments

    def get_amount_from_per_icao(self, icao):
        """
        retourne le montant actuel des assignments d'un fbo particulier
        :param ical:
        :return:
        """
        total = 0
        assignments = self.assignments.filter(fromicao=icao)
        for job in assignments:
            total += job.pay
        return total

    def get_assignments_from_per_network(self, network_name):
        """
        retourner tous les assignments actuels d'un groupe particulier
        :param network_name: le nom du réseau concerné
        :return:
        """
        list_jobs = []
        fbos = self.get_fbos_for_network(network_name)
        for fbo in fbos:
            group_assignments = {}
            group_assignments['group'] = network_name
            group_assignments['icao'] = fbo.icao
            group_assignments['nbjobs'] = self.get_nbjobs_from_per_icao(fbo.icao)
            group_assignments['amount'] = self.get_amount_from_per_icao(fbo.icao)

            list_jobs.append(group_assignments)

        return list_jobs

    def get_assignment_from_compagnie(self):
        """
        retrouver tous les assignments de la compagnie (sauf domfse)
        :return:
        """
        list_jobs = []

        for group in Accounts().get_accounts():
            if group.name != 'domfse':
                list_jobs.append(self.get_assignments_from_per_network(group.name))

        return list_jobs

    def get_infos_fbo_per_network(self, network_name):
        """
        construire la liste des dict d'infos de chaque fbo d'un network
        :param network_name:
        :return:
        """
        list_info = []
        for fbo in self.get_fbos_for_network(network_name):
            list_info.append(fbo)

        return list_info

    def get_total_transfert_amount_one_group(self, group_name=None):
        """
        retourne le montant de transfert totalisé d'un groupe donné
        Le nom du groupe apparait dans les données de bank (comment)
        :return:
        """
        amount = 0.0
        if group_name:
            transferts = Bank.objects.filter(comment__contains=group_name + ' week transfert')
            for elem in transferts:
                amount += elem.amount

        return amount

    def get_total_transfert_amount_all_group(self):
        """
        retourne le montant de transfert de chacun des groupes actifs
        dans un dict
        :return:
        """
        for g in self.group_list:
            self.group_transferts[g] = self.get_total_transfert_amount_one_group(g)

        return self.group_transferts

    def get_total_week_transfert_amount(self):
        """
        retourne le total des transferts hebdomadaire
        (comprend tous les groupes)
        :return:
        """
        total = 0.0
        dico = self.get_total_transfert_amount_all_group()
        for val in dico.values():
            total += val

        return total


class ManageNML:

    def __init__(self):
        self.nml_list = self._get_nml_list()
        self.list_pilots_active = self._get_list_active_pilot()
        self.list_pilots_all = Pilot.objects.all()
        self.dict_datas = {}
        self.cpt = 0

    def _get_nml_list(self):
        """
        retourne uniquement les groupes qui sont NML
        :return: une liste
        """
        nml = []
        lg = Network.objects.filter(nml=True)
        for g in lg:
            nml.append(g.name)
        return nml

    def update_flights(self, month=None, year=None):
        for group in self.nml_list:
            if group:
                try:
                    extract_datas_group_flights(group, month, year)
                    time.sleep(2)
                except KeyError:
                    print('Pas de donnée (NML) pour le compte', group)
            else:
                print(f'Pas de groupe {group}')

    def get_nml_datas(self):
        """
        retourne un queryset des données de la table locale (network)
        :return:
        """
        datas = Network.objects.filter(nml=True)

        return datas

    def get_nml_pilots_all_datas(self):
        return Pilot.objects.all().order_by('-actif')

    def get_date_min(self, pilot):
        data_min = GroupFlight.objects.filter(pilot=pilot).aggregate(Min('time'))
        return data_min['time__min']

    def get_date_max(self, pilot):
        data_max = GroupFlight.objects.filter(pilot=pilot).aggregate(Max('time'))
        return data_max['time__max']

    def _get_list_active_pilot(self):
        lp = []
        pilots = Pilot.objects.filter(network__pilot__actif=True)
        for pilot in pilots:
            lp.append(pilot.name)
        return lp

    def get_flights_one_nml(self, group):
        flights = GroupFlight.objects.filter(Q(groupname=group) &
                                             Q(pilot__in=self.list_pilots_active))
        return flights

    def get_total_income_one_nml(self, group):
        total = 0.0
        for flight in self.get_flights_one_nml(group):
            total += flight.income

        return total

    def get_total_pilotfee_one_nml(self, group):
        total = 0.0
        for flight in self.get_flights_one_nml(group):
            total += flight.pilotfee

        return total

    def get_total_bookingfee_one_nml(self, group):
        total = 0.0
        for flight in self.get_flights_one_nml(group):
            total += flight.bookingfee

        return total

    def get_total_gcf_one_nml(self, group):
        total = 0.0
        for flight in self.get_flights_one_nml(group):
            total += flight.gcf

        return total

    def get_total_crew_cost_one_nml(self, group):
        total = 0.0
        for flight in self.get_flights_one_nml(group):
            total += flight.crewcost

        return total

    def get_datas_one_nml(self, group):
        for gp in self.nml_list:
            self.dict_datas['groupname'] = group
            self.dict_datas['income'] = self.get_total_income_one_nml(group)

        return self.dict_datas

    def get_datas_all_nml(self):
        list_flights = []
        list_data = []
        for group in self.nml_list:
            list_flights.append(self.get_flights_one_nml(group))

        for elem in list_flights:
            for i in elem.values():
                list_data.append(i)

        return list_data

    def get_result_one_nml(self, nml):
        total = 0.0
        nb_flights = 0
        pilot = ""
        aircraft = ""
        income = 0.0
        pilot_fee = 0.0
        group_fee = 0.0
        dico_datas = {}
        results = GroupFlight.objects.filter(groupname=nml)

        for elem in results:
            aircraft = elem.aircraft
            if elem.pilot in self.list_pilots_active:
                nb_flights += 1
                pilot = elem.pilot
                income +=elem.income
                pilot_fee += elem.pilotfee
                group_fee += elem.groupfee

        dico_datas['pilot'] = pilot
        dico_datas['pilot_fee'] = pilot_fee
        dico_datas['group_fee'] = group_fee
        dico_datas['income'] = income
        if income > 0.0:
            dico_datas['rentability'] = (group_fee / income) * 100
        else:
            dico_datas['rentability'] = 0.0
        dico_datas['nb_vol'] = nb_flights
        dico_datas['aircraft'] = aircraft

        return dico_datas

    def get_result_all_nml(self):
        total = 0.0
        list_datas = []
        for group in self.nml_list:
            dico_datas = {}
            flight_number = 0
            income = 0.0
            pilot = ""
            aircraft = ""
            pilot_fee = 0.0
            group_fee = 0.0
            results = GroupFlight.objects.filter(groupname=group)
            for elem in results:
                aircraft = elem.aircraft
                if elem.pilot in self.list_pilots_active:
                    flight_number += 1
                    pilot = elem.pilot
                    income += elem.income
                    pilot_fee += elem.pilotfee
                    group_fee += elem.groupfee

            dico_datas['nml'] = group
            dico_datas['pilot'] = pilot
            dico_datas['nb_vol'] = flight_number
            dico_datas['pilot_fee'] = pilot_fee
            dico_datas['group_fee'] = group_fee
            dico_datas['income'] = income
            dico_datas['inscription'] = self.get_date_min(pilot)
            dico_datas['last_flight'] = self.get_date_max(pilot)
            if income > 0.0:
                dico_datas['rentability'] = float(group_fee) / float(income) * 100
            else:
                dico_datas['rentability'] = 0.0
            dico_datas['aircraft'] = aircraft

            list_datas.append(dico_datas)

        return list_datas


class ManageFresno:

    def __init__(self):
        self.group = 'GaugauAir California'

    def get_assignment(self):
        # vider la table
        CleanDBObject('assignment').delete_datas()

        # placer les nouvelles données
        extract_datas_assignment_group(self.group)

        # retourner le dict
        assignments = Assignment.objects.all()
        return assignments

    def get_total_assignments(self):
        total = 0.0
        assignements = self.get_assignment()
        for assignment in assignements:
            total += assignment.pay

        return total

    def get_stats(self):
        stats = Stat.objects.filter(account__contains='California')
        return stats

    def get_fbo_status(self):
        #vider la table pour ne conserver que les données de Fresno
        CleanDBObject('fbo').delete_datas()

        # placer les nouvelles données
        extract_datas_fbo(self.group)

        # retourner le dict
        fbos = Fbo.objects.all()
        return fbos

    def get_aircrafts(self):
        # vider la table aircrafts
        CleanDBObject('aircrafts').delete_datas()

        # planer les nouvelles données
        extract_datas_aircraft()

        # retourner le dict
        aircrafts = Aircraft.objects.filter(owner__contains='Californi')
        return aircrafts
