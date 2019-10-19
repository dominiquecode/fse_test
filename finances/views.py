from django.shortcuts import render
from finances.tools import *


# Create your views here.
def home(request):
    actual_loans = ManageLoan().get_loan_list().order_by('-date_begin')
    actif_loans = ManageLoan().get_loan_actif().order_by('-date_begin')
    terminated_loans = ManageLoan().get_loan_terminated().order_by('-date_begin')
    total_loans = ManageLoan().get_total_loan()
    total_paid = ManageLoan().get_actual_pay_back()
    total_due = ManageLoan().get_total_du()
    context = {'loans': actual_loans,
               'loans_actif': actif_loans,
               'loans_terminated': terminated_loans,
               'total_loan': total_loans,
               'total_paid': total_paid,
               'total_due': total_due,
               }
    return render(request, 'finances/home.html', context)


def fbo_finance(request):
    """
    afficher les états financies mensuel des FBO's
    :param request:
    :return:
    """
    return render(request, 'finances/fbo_finance.html', {})