from .tools import *


def aircrafts_test():
    CleanDBObject('aircrafts').delete_datas()
    print(len(ManageAircrafts().get_aircrafts_list()))
    extract_datas_aircraft()
    print(len(ManageAircrafts().get_aircrafts_list()))
