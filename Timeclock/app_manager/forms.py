# Std library modules
import re

# django modules
from django import forms
from django.utils import timezone


class ChangePasswordForm(forms.Form):
    class_textwidget = forms.TextInput(attrs={'class': 'form-control'})
    new_password = forms.CharField(widget=class_textwidget, max_length=80, label="New Password")
    reenter = forms.CharField(widget=class_textwidget, max_length=80, label="Re-enter")

    def clean(self):
        print 'ENTERING CLEAN'
        pattern = re.compile(r'\w+')\
        cleaned_data = super(ChangePasswordForm, self).clean()
        new_pw = cleaned_data.get("new_password")
        reentered_pw = cleaned_data.get("reenter")
        # Find match for acceptable characters
        pw_check = pattern.match(new_pw)
        if new_pw != reentered_pw:
            print 'NOT EQUAL'
            # Raise error if fields are not equal
            msg = "Password values did not match."
            raise ValueError(msg)
            # raise ValidationError(msg)
            print "And shouldn't get here."
        try:
            match = pw_check.group()
            if len(match) != len(new_pw):
                raise AttributeError
        except AttributeError:
            # Means there were unacceptable characters in the new password.
            char_msg = "Only characters A-Za-z0-9_ are allowed in a password."
            raise AttributeError(char_msg)
        return cleaned_data


class AddEmployeeForm(forms.Form):
    last_name = forms.CharField(max_length=50)
    first_name = forms.CharField(max_length=30)
    username = forms.CharField(max_length=20)
    initials = forms.CharField(max_length=4)
    street1 = forms.CharField(max_length=60, required=False)
    street2 = forms.CharField(max_length=60,required=False)
    city = forms.CharField(max_length=30, required=False)
    state = forms.CharField(max_length=2, required=False)
    zip_code = forms.CharField(max_length=10, required=False)
    date_started = forms.DateTimeField(required=False)
    starting_wage = forms.DecimalField(decimal_places=2, required=False)

    class meta:
        initial = {'date_started': timezone.now()}
