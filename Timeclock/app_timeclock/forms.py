# Django framework imports
from django import forms
from django.contrib.auth.models import User

import datetime

# Project imports
from .functions_classes import TimecardError, TimestampEntryError
from .models import Timestamp
# from models import Timestamp
# from .functions_classes import get_range, get_payperiod

# formatting widget for Bootstrap
class_textwidget = forms.TextInput(attrs={'class': 'form-control'})


class StampMixin(forms.Form):

    def __init__(self, *args, **kwargs):
        try:
            self.orig_stamp = kwargs.pop('orig_stamp')
        except KeyError:
            self.orig_stamp = None
        try:
            self.employee = kwargs.pop('employee')
        except KeyError:
            self.employee = None
        super(StampMixin, self).__init__(*args, **kwargs)

    def clean(self):
        print('IN CLEAN')
        error = False
        last = None
        cleaned_data = super(StampMixin, self).clean()
        # get the previous stamp
        if self.orig_stamp:
            last = Timestamp.objects.filter(
                user=self.orig_stamp.user,
                stamp__lt=Timestamp.objects.get(pk=self.orig_stamp.pk).stamp)
            last = last.latest('stamp')
            if last.in_out == self.cleaned_data.get('new_inout'):
                error = True
        else:
            print "clean: {0}".format(self.employee)
            last = Timestamp.objects.filter(user=self.employee).latest('stamp')
            if last.in_out == self.cleaned_data.get('in_out'):
                error = True

        # l_stamp = last.stamp
        # print "{} -- {}".format(last.in_out, l_stamp)
        # print self.cleaned_data['new_inout']
        if error:
            raise TimestampEntryError('IN/OUT not in correct order.')

        return cleaned_data


class TimestampForm(StampMixin):
    """
    Form for generating new timestamp.
    """
    class_selectwidget = forms.Select(attrs={'class': 'form-control'})
    sel_widget = class_selectwidget
    CHOICES = (('IN', 'IN'), ('OUT', 'OUT'))
    stamp = forms.DateTimeField(widget=class_textwidget)
    in_out = forms.ChoiceField(choices=CHOICES, widget=sel_widget)


class NoUserTimestampForm(TimestampForm):
    """
    The NoUserTimestampForm allows entry without authentication. An employee
    enters their username into the 'Username' field to determine User instance
    to clock in or out.

    NoUserTimestampForm inherits from TimestampForm inherits from StampMixin
    """
    class_selectwidget = forms.Select(attrs={'class': 'form-control'})
    # add username text entry field
    employee = forms.CharField(max_length=30, widget=class_textwidget)



class EditStampForm(StampMixin):
    """
    The EditStampForm is used to enter a date and and In/Out state to be used
    in updating a Timestamp instance. When used in conjunction with an
    appropriate view, such as the provided vw_edit_timestamp view, can be used
    to change the stamp and in_out attributes of a Timestamp instance.

    The clean method for the form is derived from the superclass StampMixin to
    check for correct In/Out ordering, and can not be validated unless the
    new values fit within the correct ordering structure of IN/OUT/IN/OUT. . .
    """
    class_selectwidget = forms.Select(attrs={'class': 'form-control'})
    class_textareawidget = forms.Textarea(attrs={'class': 'form-control'})
    sel_widget = class_selectwidget
    new_datetime = forms.DateTimeField(widget=class_textwidget)
    CHOICES = (('IN', 'IN'), ('OUT', 'OUT'))
    new_inout = forms.ChoiceField(choices=CHOICES, widget=sel_widget)
    change_reason = forms.CharField(max_length=255, widget=class_textareawidget)


class EmpViewTimecardForm(forms.Form):
    """
    The EmpViewTimecardForm displays one field that collects a date input.
    """
    date = forms.DateTimeField(widget=class_textwidget)


class ManagerViewTimecardForm(forms.Form):
    """
    The ManagerViewTimecardForm displays one select widget and one text entry
    field for requiring input of a date.

    The form generates a selected User instance and a date.
    """
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

