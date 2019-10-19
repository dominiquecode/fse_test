# les filtres personnalisés utilisés dans l'application
from django import template

register = template.Library()


@register.filter
def float_string(value, nb='2'):
    """
    filtre d'affichage des valeurs Float en string avec espace et virgule
    :param value: la valeur à formater
    :param nb: le nombre de décimal à afficher (par défaut : 2)
    :return: la valeur formatée
    """
    if value:
        if nb == '0':
            return "{:,.0f}".format(value).replace(',', ' ').replace('.', ',')
        else:
            return "{:,.2f}".format(value).replace(',', ' ').replace('.', ',')
    else:
        return 0.0
