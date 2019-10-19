# procédures de mise à jour pour regrouper tous les éléments
# et les répartir dans le temps afin de respecter les limitations
# du serveur FSE
# 10 requêtes par minutes et
# 40 requêtes par 6 heures

# from avion.tools import *
# from finances.tools import *
import time
from django.utils import timezone
from avion.tools import *
from network.tools import *


# TODO permettre de choisir le mois de travail de la procédure
class UpdateFSE:
    """
    Cette classe gère la mise à jour des données de GaugauAir à partir du serveur de FSE
    les limitations de connexion vers le serveur FSE implique de temporiser le déroulement
    de la procédure de mise à jour.

    les limitations sont : 10 connexions en 60 secondes et 40 connexions en 6 heures

    Pour une mise à jour des données pour un mois particulier, il suffit de donner le
    paramètre mois (valeur de 1 à 12) à la création de l'objet UpdateFSE, sinon c'est le mois courant qui
    est utilisé.
    """

    def __init__(self, month=None):
        if month is None:
            self.month = timezone.now().month
        else:
            self.month = month

    # @mesurer_temps(1)
    def update_gaugauair(self):
        """
        mise à jour générale des données à partir des serveurs de FSE
        Procédure centrale de mise à jour pour limiter les impacts
        sur le serveur et tenir compte des limites des clefs d'accès.
        :return: message log sur le déroulement de la procédure
        """
        time_debut = timezone.now()
        print('************************************')
        print('Début de la procédure de mise à jour')
        print(f"Heure de démarrage : {time_debut}")
        print('************************************')
        print('*')

        self.update_bank(2)

        # self.update_stats(2)

        # self.update_flights(2)

        # self.update_aircrafts(2)

        # self.update_fbos(2)

        # self.update_facilities(2)

        # self.update_nml(2)

        # self.update_assignments(2)

        time_fin = timezone.now()
        duree = time_fin - time_debut
        print('**************************************************************')
        print(f"fin de la procédure de mise à jour")
        print(f"heure de fin : {time_fin}")
        print(f"Durée totale de la procédure : {duree}")
        print('**************************************************************')

    # @mesurer_temps(1)
    def update_assignments(self, interval):
        """
        procédure centrale de mise à jour des assignments (FROM) de la compagnie

        :param interval:
        :return: None
        """
        start = timezone.now()
        print('update assignments start:', timezone.now())
        ManageAssignments().update()
        print('update assignments end:', timezone.now())
        end = timezone.now()
        duree = end - start
        print('Durée de la procédure assignments:', str(duree))
        time.sleep(interval)
        print('')

    # @mesurer_temps(1)
    def update_nml(self, interval):
        """
        procédure centrale de mise à jour des nml de la compagnie

        :param interval:
        :return: None
        """
        start = timezone.now()
        print('update nml start:', timezone.now())
        ManageNML().update_flights(self.month)
        print('update nml end:', timezone.now())
        end = timezone.now()
        duree = end - start
        print('Durée de la procédure NML:', str(duree))
        time.sleep(interval)
        print('')

    # @mesurer_temps(1)
    def update_stats(self, interval):
        """
        procédure centrale de mise à jour des stats de la compagnie

        :param interval:
        :return: None
        """
        start = timezone.now()
        print('update stats start:', timezone.now())
        ManageStats(self.month).update()
        print('update stat end:', timezone.now())
        end = timezone.now()
        duree = end - start
        print('Durée de la procédure stats:', str(duree))
        time.sleep(interval)
        print('*')

    # @mesurer_temps(1)
    def update_bank(self, interval):
        depart = timezone.now()
        print('*')
        print('update bank depart:', timezone.now())
        ManageBank(month=self.month).update()
        fin = timezone.now()
        print('update bank fin:', timezone.now())
        print('Durée de la procédure bank:', fin - depart)
        time.sleep(interval)
        print('*')

    # @mesurer_temps(1)
    def update_flights(self, interval):
        start = timezone.now()
        print('')
        print('update flights', start)
        ManageFlights().update(month=self.month)
        end = timezone.now()
        duree = end - start
        print('Durée de la procédure flights :', str(duree))
        time.sleep(interval)
        print('')

    # @mesurer_temps(1)
    def update_aircrafts(self, interval):
        start = timezone.now()
        print('update aircrafts depart:', start)
        ManageAircrafts().update_aircrafts_use_datas()
        end = timezone.now()
        print('update aircrafts fin:', end)
        duree = end - start
        print('durée de la procédure aircrafts : ', str(duree))
        time.sleep(interval)
        print('')

    # @mesurer_temps(1)
    def update_fbos(self, interval):
        start = timezone.now()
        print('update fbos depart:', start)
        ManageFbos().update_list()
        end = timezone.now()
        print('update fbos fin : ', end)
        duree = end - start
        print('durée de la procédure fbo : ', str(duree))
        time.sleep(interval)
        print('')

    # @mesurer_temps(1)
    def update_facilities(self, interval):
        start = timezone.now()
        print('update facilities', start)
        ManageFacilities().update_list()
        end = timezone.now()
        print('update facilities fin : ', end)
        duree = end - start
        print('Durée de la procédure facilities : ', str(duree))
        time.sleep(interval)
        print('')
