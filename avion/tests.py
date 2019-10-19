from django.test import TestCase
from .models import *
from .tools import *
# from avion.couchetravail import ExtractionDatas
# Create your tests here.


class TestAvion(TestCase):

    nb_avion_actuel = Aircraft.objects.count()

    def test_nb_avion(self):
        avions = ManageAircrafts().get_aircrafts_list()
        self.assertEqual(len(avions), self.nb_avion_actuel)

    def test_vider_db_avion(self):
        # vérifier la flotte actuelle
        avions = ManageAircrafts().get_aircrafts_list()
        nb_test = len(avions)
        # vider la bd
        CleanDBObject('aircrafts').delete_datas()
        nb_vide = len(Aircraft.objects.all())
        # tester
        self.assertEqual(nb_test, self.nb_avion_actuel)
        self.assertEqual(nb_vide, 0)

    def test_avion_retraite(self):
        avions = AircraftRetired.objects.all()
        self.assertIsNotNone(avions, msg="Pas d'avion en retraite")


class TestExtraction(TestCase):

    def setUp(self):
        self.account = ['domfse', 'GaugauAir Durant']
        self.data_type = ['fbo_for_sale', 'aircrafts', 'bank', 'fbo']

    def test_transfert_datas_to_list(self):
        for acc in self.account:
            for t in self.data_type:
                dico = ExtractionDatas(t, acc).get_datas()
                self.assertIsInstance(dico, list, msg="Datas extract error")

    def test_clean_db_object(self):
        Fbo.objects.create(fboid=1,)
        self.assertEqual(Fbo.objects.count(), 1)

        CleanDBObject('fbo').delete_datas()
        self.assertEqual(Fbo.objects.count(), 0, msg='cleaning error')

    def test_default_date(self):
        dico = ExtractionDatas('aircrafts')
        self.assertEqual(dico.month, timezone.now().month)
        self.assertEqual(dico.year, timezone.now().year)

    def test_valide_date(self):
        dico = ExtractionDatas('aircrafts', 'domfse', 5, 2018)
        self.assertEqual(dico.month, 5)
        self.assertEqual(dico.year, 2018)

    def test_default_account(self):
        dico = ExtractionDatas('aircrafts')
        self.assertEqual(dico.account, 'domfse')

    def test_valide_account(self):
        dico = ExtractionDatas('aircrafts', 'GaugauAir')
        self.assertEqual(dico.account, 'GaugauAir')
