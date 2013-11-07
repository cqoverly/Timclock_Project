# Django framework imports
from django import forms
from django.contrib.auth.models import User

import datetime

# Project imports
from .functions_classes import TimecardError, TimestampEntryError
# from models import Timestamp
# from .functions_classes import get_range, get_payperiod

# formatting widget for Bootstrap
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

    # TODO: Define clean of TimestampForm to check for consistent in_out
    def clean(self):
        cleaned_data = super(TimestampForm, self).clean()
        return cleaned_data


class EditStampForm(forms.Form):
    class_selectwidget = forms.Select(attrs={'class': 'form-control'})
    class_textareawidget = forms.Textarea(attrs={'class': 'form-control'})
    sel_widget = class_selectwidget
    new_datetime = forms.DateTimeField(widget=class_textwidget)
    CHOICES = (('IN', 'IN'), ('OUT', 'OUT'))
    new_inout = forms.ChoiceField(choices=CHOICES, widget=sel_widget)
    change_reason = forms.CharField(max_length=255, widget=class_textareawidget)

    # TODO: Define clean of EditTimestampForm to check for consistent in_out
    def clean(self):
        cleaned_data = super(EditStampForm, self).clean()
        return cleaned_data


class EmpViewTimecardForm(forms.Form):
    date = forms.DateTimeField(widget=class_textwidget)


class ManagerViewTimecardForm(forms.Form):
    # get list of employees
    employees = User.objects.filter(groups__name='Employee')
    # formatting widget for Bootstrap
    class_selectwidget = forms.Select(attrs={'class': 'form-control'})
    name = forms.ModelChoiceField(queryset=employees,
        widget=class_selectwidget)
    date = forms.DateTimeField(widget=class_textwidget)

class EmpViewTimestampListForm(forms.Form):
    start_date = forms.DateField(label="Start", widget=class_textwidget)
    end_date = forms.DateField(label="End", widget=class_textwidget)

class MgrViewTimestampListForm(forms.Form):
    # get list of employees
    emps = User.objects.filter(groups__name="Employee")
    # custom widget needs to be reinitialized.
    class_selectwidget = forms.Select(attrs={'class': 'form-control'})
    employee = forms.ModelChoiceField(
        widget=class_selectwidget,
        queryset=emps,
        label="Employee")
    start_date = forms.DateField(label="Start")
    end_date = forms.DateField(label="End")

