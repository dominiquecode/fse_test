"""fse URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from .views import accueil, enregistrements, facilities, \
    stats, aircrafts, flights, fbos, formulaire, jobs, aircrafts_retired, \
    fbos_for_sale, vols, aircrafts_cost

app_name = 'avion'

urlpatterns = [
    path('', accueil, name='accueil'),
    # path('update/', update, name='update'),
    # path('importation/', importation, name='importation'),
    # path('affichage/retraite', retraite, name='retraite'),
    path('enregistrements/', enregistrements, name='enregistrements'),
    # path('retraite/', sortir_avion, name='sortir_avion'),
    # path('usage/', usage, name='usage'),
    # path('assignement/', fbo_assignements, name='assignements'),
    # path('fbo/', fbo, name='fbo'),
    path('facilities/', facilities, name='facilities'),
    path('stats/', stats, name='stats'),
    path('aircrafts/', aircrafts, name='aircrafts'),
    path('aircrafts_cost/', aircrafts_cost, name='aircrafts_cost'),
    path('flights/', flights, name='flights'),
    path('fbos/', fbos, name='fbos'),
    path('fbosSale/', fbos_for_sale, name='fbos_for_sale'),
    path('jobs/', jobs, name='jobs'),
    path('formulaire/', formulaire, name='formulaire'),
    path('retired/', aircrafts_retired, name='retired'),
    path('vols/', vols, name='vols'),
]
