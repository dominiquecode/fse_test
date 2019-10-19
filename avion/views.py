from django.shortcuts import render
from django.db.models.query import QuerySet
# from .tools import mesurer_temps
from .update_fse import *
from .models import Bank, AircraftRetired, Use, Assignment, Fbo
from django.db.models import Sum
from .forms import SelectionAvionForm


# from django.db.models.functions import Trunc


# Create your views here.

# test sentry debugger
#
# def trigger_error(request):
#     division_by_zero = 1 / 0


def accueil(request):
    if request.POST.get('maj'):
        UpdateFSE().update_gaugauair()

    aircrafts = ManageAircrafts().get_aircrafts_list()
    fbos = ManageFbos().get_list()
    context = {'aircrafts': aircrafts,
               'fbos': fbos,
               }
    return render(request, "avion/accueil.html", context)


# @mesurer_temps(1)
def stats(request):
    """
    update stats datas
    :param request:
    :return:
    """
    if request.POST.get('update'):
        ManageStats().update()

    if request.POST.get('update_dva'):
        ManageJobs().update_dva_week()

    statistics = ManageStats().get_list()
    investissements_fbo = ManageFacilities().get_investissement_total()
    profit_avion = ManageAircrafts().get_profit_total()
    cash_available = ManageStats().get_cash_amount()
    # incomes_a2b = ManageJobs().get_a2b_jobs()
    incomes_dva = ManageJobs().get_dva_jobs()
    incomes_dva_week_current = ManageJobs().get_dva_jobs_week_current()
    incomes_oac = ManageJobs().get_oac_jobs()
    flights_challenge = ManageFlights().get_challenge_info()
    recap_challenge = ManageFlights().get_challenge_recap()
    last_date = ManageBank().get_last_date()
    context = {'statistics': statistics,
               'profits_avion': profit_avion,
               'investissement_fbo': investissements_fbo,
               'cash_available': cash_available,
               # 'a2b_jobs': incomes_a2b,
               'dva_jobs': incomes_dva,
               'dva_jobs_week_current': incomes_dva_week_current,
               'oac_jobs': incomes_oac,
               'flights_challenge': flights_challenge,
               'recap_challenge': recap_challenge,
               'last_date': last_date,
               }
    return render(request, 'avion/stats.html', context)


def aircrafts(request):
    """
    update aircrafts general datas
    :param request:
    :return:
    """
    if request.POST.get('update_list'):
        ManageAircrafts().update_list()
        ManageFlights().update()

    if request.POST.get('update_use'):
        ManageAircrafts().update_aircrafts_use_datas()

    aircrafts_list = ManageAircrafts().get_aircrafts_actif_list()
    # aircrafts_cost = ManageAircrafts().get_use_datas()
    monthlyfee_cost = ManageAircrafts().get_total_monthly_fee()
    # profit_total = ManageAircrafts().get_profit_total()
    last_date = ManageBank().get_last_date()
    context = {'aircrafts_list': aircrafts_list,
               # 'aircrafts_cost': aircrafts_cost,
               'monthlyfee_cost': monthlyfee_cost,
               # 'profit_total': profit_total,
               'last_date': last_date}
    return render(request, 'avion/aircrafts.html', context)


def aircrafts_cost(request):
    """
    obtenir les coûts et bénéfices par avion
    :param request:
    :return:
    """
    if request.POST.get('update_use'):
        ManageAircrafts().update_aircrafts_use_datas()

    ac_cost = ManageAircrafts().get_use_datas()
    profit_total = ManageAircrafts().get_profit_total()
    last_date = ManageBank().get_last_date()
    context = {'aircrafts_cost': ac_cost,
               'profit_total': profit_total,
               "last_date": last_date}

    return render(request, 'avion/aircrafts_cost.html', context)


def aircrafts_retired(request):
    """
    show retired environment
    :param request:
    :return:
    """
    acs = ManageAircrafts().get_aircrafts_list()
    context = {'aircrafts': acs}
    return render(request, 'avion/aircrafts_retired.html', context)


def fbos(request):
    """
    update FBO's datas™
    :param request:
    :return:
    """
    if request.POST.get('update_list'):
        ManageFbos().update_list()

    fbos_infos = ManageGroup().get_infos_fbo_per_network('GaugauAir Chambers')
    fbos_list = ManageFbos().get_list()
    last_date = ManageBank().get_last_date()
    context = {'fbos_list': fbos_list,
               'last_date': last_date,
               'chambers': fbos_infos}
    return render(request, 'avion/fbos.html', context)


def fbos_for_sale(request):
    """
    show fbo's for sale for a specific location
    :param request:
    :param location:
    :return:
    """
    if request.method == "POST":
        location = request.POST.get('localisation')
        fbos_list = ManageFbos().get_fbo_for_sale_localisation(location)
        context = {'fbos_list': fbos_list,
                   'location': location,
                   }
    else:
        context = {}
    return render(request, 'avion/fbovente.html', context)


def facilities(request):
    """
    Update Facilities datas
    :param request:
    :return:
    """
    if request.POST.get('update'):
        ManageFacilities().update_list()

    fac = ManageFacilities().get_list().order_by('-profits')
    rent_cost = ManageFacilities().get_total_monthly_rent_cost()
    incomes_total = ManageFacilities().get_incomes_total()
    profits_total = abs(ManageFacilities().get_profit_total())
    return_rate = ManageFacilities().get_incomes_total() / abs(ManageFacilities().get_profit_total()) * 100
    last_date = ManageBank().get_last_date()

    context = {'facilities': fac,
               'profits': profits_total,
               'incomes': incomes_total,
               'return_rate': return_rate,
               'rent_costs': rent_cost,
               'last_date': last_date}
    return render(request, 'avion/facilities.html', context)


def enregistrements(request):
    if request.POST.get('update'):
        ManageBank().update()

    datas = Bank.objects.all().order_by("-date_item")[:300]
    last_date = ManageBank().get_last_date()
    context = {'datas': datas,
               'last_date': last_date
               }
    return render(request, 'avion/enregistrements.html', context)


def jobs(request):
    accounts = Accounts().get_list_accounts()
    context = {'accounts': accounts}
    return render(request, 'avion/jobs.html', context)


def formulaire(request):
    fbos = ManageFbos().get_list_icao()
    context = {'fbos': fbos}
    return render(request, 'avion/formulaire.html', context)


def flights(request):
    context = {}

    if request.method == "POST":

        last_date = ManageBank().get_last_date()
        actual_registration = request.POST.get('aircraft')
        print(f"Immat actual : {actual_registration}")
        if request.POST.get('modify_registration'):
            actual_registration = request.POST.get('registration_source')
            new_registration = request.POST.get('registration')
            print(f"Immat source : {actual_registration}")
            print(f"Immat future : {new_registration}")
            ManageAircrafts().change_registration(actual_registration, new_registration)
            registration = new_registration
        else:
            registration = actual_registration

        print(f"Immat utile : {registration}")
        aircraft_obj = ManageAircrafts().get_by_registration(registration)
        aircraft_flights = ManageFlights().get_last_50_by_registration(registration)
        leaser = ManageFlights().get_lease_from(registration)
        income_total = ManageFlights().get_total_income_by_registration(registration)
        flight_time_total = ManageFlights().get_total_flight_time_by_registration(registration)
        ratio_by_nm = ManageFlights().get_ratio_by_nm(registration)
        ratio_by_hour = ManageFlights().get_ratio_by_hour(registration)
        ratio_finance = ManageFlights().get_ratio_financial(registration)
        context = {'aircraft': aircraft_obj,
                   'flights': aircraft_flights,
                   'last_date': last_date,
                   'income_total': income_total,
                   'flight_time_total': flight_time_total,
                   'ratio_by_hour': ratio_by_hour,
                   'ratio_by_nm': ratio_by_nm,
                   'ratio_finance': ratio_finance,
                   'leaser': leaser,
                   }

    return render(request, 'avion/flights.html', context)


def vols(request):
    context = {}
    avion = ''
    fbo = ''

    # bouton 'Mettre à jour' (dansla base de données locale)
    if request.POST.get('update'):
        ManageFlights().update()

    # bouton "Vols" pour trouver les dix derniers vols d'un avion
    if request.POST.get('lookup'):
        avion = request.POST.get('registration', 'Problème avec le formulaire de saisie')

        vols = ManageFlights().get_by_registration(avion)[:10]

        context = {'avion': avion,
                   'flights': vols,
                   }

    # bouton 'Confirmer" pour trouver les données d'une sous-ensemble de vols
    if request.POST.get('confirm'):
        start = request.POST.get('start')
        stop = request.POST.get('stop')

        result = ManageFlights().get_by_ids(start, stop)
        vols = ManageFlights().get_by_registration(avion)[:10]

        context = {'test': 'lookup : OK',
                   'results': result,
                   'flights': vols}

    return render(request, 'avion/vols.html', context)
