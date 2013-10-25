from django import forms
from django.contrib.auth.models import User, Group

from models import Timestamp
import datetime

# formatting wisdget for Bootstrap
class_textwidget = forms.TextInput(attrs={'class': 'form-control'})

class TimestampForm(forms.Form):
    # formatting widger for Bootstrap
    class_selectwidget = forms.Select(attrs={'class': 'form-control'})
    sel_widg = class_selectwidget
    CHOICES = (('IN', 'IN'), ('OUT', 'OUT'))
    stamp = forms.DateTimeField(widget=class_textwidget)
    in_out = forms.ChoiceField(choices=CHOICES, widget=sel_widg)


class EmpViewTimecardForm(forms.Form):
    # name = forms.ModelChoiceField(queryset=Employee.objects.all())
    date = forms.DateTimeField(widget=class_textwidget)


class ManagerViewTimecardForm(forms.Form):
    # get list of employees
    employees = User.objects.filter(groups__name='Employee')
    # formatting widger for Bootstrap
    class_selectwidget = forms.Select(attrs={'class': 'form-control'})
    name = forms.ModelChoiceField(queryset=employees,
        widget=class_selectwidget)
    date = forms.DateTimeField(widget=class_textwidget)
