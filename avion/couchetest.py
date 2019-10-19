# le fichier pour tester les classes en développement

# importation
from .tools import *
from .models import Aircraft


# procedures
def get_aircraft_financial_state(registration):
    """
    procédure pour récupérer les indicateurs financiers d'un avion particulier
    dont l'icao est passé en paramètre
    :param registration:
    :return: un dictionnaire contenant les indicateurs financiers
    """
    dico = {'registration': '',
            'makemodel': '',
            'owner': '',
            'home':'',
            'location': '',
            'last100': '',
            'leasedfrom': '',
            'monthlyfee': '',
            }
    aircraft_info = Aircraft.objects.get(registration=registration)

    print(aircraft_info)

    return aircraft_info

