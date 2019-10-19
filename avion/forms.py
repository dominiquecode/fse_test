from django import forms
from .models import Aircraft


class SelectionAvionForm(forms.Form):
    Selection = forms.CharField(widget=forms.Select)


class AircraftInfoForm(forms.ModelForm):
    class Meta:
        model = Aircraft
        fields = ['makemodel', 'registration', 'airframe_time', 'monthlyfee']