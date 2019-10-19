from django.shortcuts import render
from .tools import *


# Create your views here.
def nml(request):
    if request.POST.get('update_nml'):
        ManageNML().update_flights()

    # nml_pilots = ManageNML().list_pilots_active
    # nml_groups = ManageNML().nml_list
    nml_pilots_historique = ManageNML().get_nml_pilots_all_datas()
    nml_flights = ManageNML().get_datas_all_nml()
    nml_results = ManageNML().get_result_all_nml()
    context = {'nml_flights': nml_flights,
               # 'nml_pilots': nml_pilots,
               # 'nml_groups': nml_groups,
               'nml_results': nml_results,
               'nml_pilots_historique': nml_pilots_historique,
               }
    return render(request, 'network/nml_resultats.html', context)


def fresno(request):
    """
    les données de l'essai de Fresno Californie
    :param request:
    :return:
    """
    facilities = ManageFresno().get_assignment()
    total_assignments = ManageFresno().get_total_assignments()
    stats = ManageFresno().get_stats()
    management = ManageFresno().get_fbo_status()
    aircrafts = Aircraft.objects.filter(owner__contains='Californi')
    context = {'facilities': facilities,
               'total_assignments': total_assignments,
               'stats': stats,
               'management': management,
               'aircrafts': aircrafts,
               }
    return render(request, 'network/fresno.html', context)


def groups(request):
    groups = ManageGroup().get_total_transfert_amount_all_group()
    total = ManageGroup().get_total_week_transfert_amount()
    context = {'groupes': groups,
               'total_transfert': total
               }
    return render(request, 'network/group_income.html', context)


def description(request):
    nml_groups = ManageNML().get_nml_datas()
    context = {'nml_groups': nml_groups.filter(nml=True),
               }
    return render(request, 'network/description.html', context)


def assignement(request):
    return render(request, 'network/assignement.html', {})


def pax(request):
    if request.method == "POST":
        network_name = request.POST.get('group')
        pax = ManageGroup().get_assignments_from_per_network(network_name)
        context = {'pax': pax,
                   'group': network_name
                   }
    else:
        context = {}

    return render(request, 'network/pax.html', context)



