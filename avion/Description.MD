# GaugauAir

## Description générale
Un site web qui permet de gérer les données extraites du serveur de FSE 
(FSEconomy).
Les données sont transformées pour répondre aux besoins d'analyse de 
GaugauAir afin de développer au mieux la compagnie aérienne.

## plan du site
- Une page d'accueil pour sélectionner les paramètres à prendre en compte pour l'analyse. On peut envisager pour plus tard un tableau de bord complet qui donnera l'état de santé général de la compagnie.

- Une page pour la représentation de l'état des avoirs de la compagnie. Les avoirs actuels et passés.
- etc ...

## les outils de travail
### la couche de données
- un avion
- un vol
- un assignement
- un fbo
- une information financière (les finances de la compagnie)
- un compte (domfse - GaugauAir)
### la couche de travail
#### extraction des données
- récupérer toutes les données sur le serveur fse telles qu'elles existent sur le serveur. (pas de transformation)
- placer les données extraites dans les tables de l'application locale telles quelles (données brutes)

#### préparation des données locales en vue de l'affichage
- transformation des données locales en fonction des besoins d'affichage

#### affichage des données sur le site local
- envoyer les données dans les templates par les views.


- historique de la flotte
- historique des FBO's
    - récupérer tous les fbo's en vente et pouvoir filtrer sur une région et/ou un aéroport particulier pour faire de la recherche des disponibilités.

- les avions en activité
- les avions retraités (ventes ou fin de leasing)
- comportement financier des avions
- les vols générés par les portes (louées ou - - - propriétaire)
- calculs des coûts et revenus (par avion, par FBO)
- calcul des profits
- mettre à jour toutes les données en fonction d'un mois et d'une année particulière

### la couche d'affichage
- États financiers de la compagnie
- liste des FBO's (porte ou bâtiment) en activité
- Liste des avions en activité
- liste des avions retraités
- table de répartition des coûts et revenus par avion
- les résultats financiers d'un avion particulier
- les résultats financiers d'un FBO particulier
- les FBO à vendre dans une région particulière
- mettre à jour les données en choisissant un mois particulier