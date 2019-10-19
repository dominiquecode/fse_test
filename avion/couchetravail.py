# les classes de travail de l'application
from urllib.request import urlopen
import xmltodict


# class ExtractionDatas:
#     """
#     Établir une connexion avec le serveur fse
#     à partir d'une URL (requête)
#     de la clef d'un compte (domfse ou GaugauAir)
#     pour un mois et une année particulière
#     (valeur par défaut : mois=7, année=2018
#
#     """
#     def __init__(self, data_type, account='domfse', month=7, year=2018):
#         # le dictionnaire des comptes utilisés par l'application
#         _accounts = {'domfse': 'E5VXW4KYE0',
#                    'gaugauair': '81AEJZ6MMW', }
#
#         # les variables de travail de la classe
#         self.data_type = data_type
#         self.account = account
#         self.month = month
#         self.year = year
#         self.key = _accounts[self.account]
#         self.url = self._build_url()
#
#     def _build_url(self):
#         """
#         construire l'URL utilisée par la requête sur le serveur de FSE
#
#         :return: la requête sous forme de chaine de caractère
#         """
#
#         if self.data_type == 'bank':
#             self.url = 'http://server.fseconomy.net/data?userkey=' + self.key + \
#                        '&format=xml&query=payments&search=monthyear&readaccesskey=' + \
#                        self.key + '&month=' + str(self.month) + '&year=' + str(self.year)
#         elif self.data_type == 'aircrafts':
#             self.url = 'http://server.fseconomy.net/data?userkey=' + self.key + \
#                        '&format=xml&query=aircraft&search=ownername&ownername=' + self.account
#         elif self.data_type == 'fbo':
#             self.url = 'http://server.fseconomy.net/data?userkey=' + self.key + \
#                        '&format=xml&query=Facilities&search=key&readaccesskey=' + self.key
#         elif self.data_type == 'fbo_for_sale':
#             self.url = 'http://server.fseconomy.net/data?userkey=' + self.key + \
#                        '&format=xml&query=fbos&search=forsale'
#
#         return self.url
#
#     def extract_datas(self):
#         """
#         connecte le serveur fse avec l'URL et retourne les données
#         sous forme de dictionnaire
#
#         :param:
#         :return: les données recherchées sous forme de dictionnaire
#         """
#
#         file = urlopen(self.url)
#         data = file.read()
#         file.close()
#         datas = xmltodict.parse(data)
#
#         return datas

