from django import forms
from django.contrib.auth.models import User, Group

from models import Timestamp
import datetime

# Project imports
from .functions_classes import get_range, get_payperiod

# formatting wisdget for Bootstrap
class_textwidget = forms.TextInput(attrs={'class': 'form-control'})

class TimestampForm(forms.Form):
    """
    Form for generating new timestamp.
    """
    class_selectwidget = forms.Select(attrs={'class': 'form-control'})
    sel_widget = class_selectwidget
    CHOICES = (('IN', 'IN'), ('OUT', 'OUT'))
    stamp = forms.DateTimeField(widget=class_textwidget)
    in_out = forms.ChoiceField(choices=CHOICES, widget=sel_widget)


class EditStampForm(forms.Form):
    class_selectwidget = forms.Select(attrs={'class': 'form-control'})
    sel_widget = class_selectwidget
    new_datetime = forms.DateTimeField()
    CHOICES = (('IN', 'IN'), ('OUT', 'OUT'))
    new_inout = forms.ChoiceField(choices=CHOICES, widget=sel_widget)
    change_reason = forms.CharField(max_length=255, widget=class_textwidget)

    # def clean(self):
    #     cleaned_data = super(EditStampForm, self).clean()
    #     original_stamp = cleaned_date('timestampID')
    #     new_date = cleaned_data.get('new_datetime')
    #     new_inout = cleaned_data.get('new_inout')
    #     employee = original_stamp.employee
    #     date_start, date_end = get_payperiod(new_date.date()).order_by('stamp')
    #     # get a the payperiod into which we are trying to add updated stamp
    #     check_range = get_range(employee, date_start, date_end)
    #     # create a duplicate list of stamps in returned query result
    #     test_newrange = check_range[:]
    #     # find original
    #     stamp_idx = test_newrange.index(original_stamp)





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


