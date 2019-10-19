from avion.tools import *


def facilities_bank():
    facilities = Bank.objects.filter(fbo__contains='T41').aggregate(Sum('amount'))
    print(facilities['amount__sum'])




def extraire_bank():
    item = Bank.objects.filter(ident=92996075)
    print(item)
