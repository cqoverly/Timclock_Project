# Std library modules
import re

# django modules
from django import forms
from django.utils import timezone


class ChangePasswordForm(forms.Form):
    """
    Standard style enter and re-enter password form.
    """
    class_textwidget = forms.TextInput(attrs={'class': 'form-control'})
    new_password = forms.CharField(
        widget=class_textwidget,
        max_length=80,
        label="New Password"
    )
    reenter = forms.CharField(
        widget=class_textwidget,
        max_length=80,
        label="Re-enter"
    )

    def clean(self):
        """
        Checks for allowable characters and field matches for entry and
        re-entry.

        Raises custom exception as AttributeError with message which can be
        used in receiving function.
        """
        pattern = re.compile(r'\w+')
        cleaned_data = super(ChangePasswordForm, self).clean()
        new_pw = cleaned_data.get("new_password")
        reentered_pw = cleaned_data.get("reenter")
        # Find match for acceptable characters
        pw_check = pattern.match(new_pw)
        if new_pw != reentered_pw:
            # Raise error if fields are not equal
            msg = "Password values did not match."
            raise ValueError(msg)
        try:
            match = pw_check.group()
            if len(match) != len(new_pw):
                raise AttributeError
        except AttributeError:
            # Means there were unacceptable characters in the new password.
            char_msg = "Only characters A-Za-z0-9_ are allowed in a password."
            raise AttributeError(char_msg)
        return cleaned_data


class EmployeeInfoForm(forms.Form):
    """
    Used to generate both a new django User, as well as an an Employee instance
    """
    class_textwidget = forms.TextInput

    last_name = forms.CharField(
        max_length=50,
        widget=class_textwidget(attrs={'class': 'form-control'})
    )
    first_name = forms.CharField(
        max_length=30,
        widget=class_textwidget(attrs={'class': 'form-control'})
    )
    username = forms.CharField(
        max_length=20,
        widget=class_textwidget(attrs={'class': 'form-control'})
    )
    street1 = forms.CharField(
        max_length=60,
        required=False,
        widget=class_textwidget(attrs={'class': 'form-control'})
    )
    street2 = forms.CharField(
        max_length=60,
        required=False,
        widget=class_textwidget(attrs={'class': 'form-control'})
    )
    city = forms.CharField(
        max_length=30,
        required=False,
        widget=class_textwidget(attrs={'class': 'form-control'})
    )
    state = forms.CharField(
        max_length=2,
        required=False,
        widget=class_textwidget(attrs={'class': 'form-control'})
    )
    zip_code = forms.CharField(
        max_length=10,
        required=False,
        widget=class_textwidget(attrs={'class': 'form-control'})
    )
    date_started = forms.DateTimeField(
        required=False,
        widget=class_textwidget(attrs={'class': 'form-control'})
    )
    starting_wage = forms.DecimalField(
        decimal_places=2,
        required=False,
        widget=class_textwidget(attrs={'class': 'form-control'})
    )
    current_wage = forms.DecimalField(
        decimal_places=2,
        required=False,
        widget=class_textwidget(attrs={'class': 'form-control'})
    )

    class meta:
        initial = {'date_started': timezone.now()}
