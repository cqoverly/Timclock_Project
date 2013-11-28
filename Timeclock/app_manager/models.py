from django.contrib.auth.models import User, Group
from django.db import models

from localflavor.us.models import USStateField, USPostalCodeField

# Create your models here.

class Employee(models.Model):
    user = models.ForeignKey(User)
    street1 = models.CharField(max_length=60, null=True, blank=True,)
    street2 = models.CharField(max_length=60, null=True, blank=True,)
    city = models.CharField(max_length=30, blank=True,)
    state = USStateField(null=True, blank=True,)
    zip_code = USPostalCodeField(null=True, blank=True,)
    date_started = models.DateField(null=True, blank=True,)
    date_ended = models.DateField(null=True, blank=True,)
    starting_wage = models.DecimalField(null=True,
        max_digits=6,
        decimal_places=2,
        blank=True,
    )
    current_wage = models.DecimalField(null=True,
        max_digits=6,
        decimal_places=2,
        blank=True,
    )

    class meta:
        ordering = ['user.last_name', 'user.first_name']

    def __str__(self):
        template = '{} {}\nDate Started: {}\nCurrent Wage: {}'
        return template.format(
            self.user.first_name,
            self.user.last_name,
            self.date_started,
            self.current_wage,
        )

    @classmethod
    def add_employee(cls, attrs):
        params = attrs
        # create new django.contrib.auth.models.User instance for new employee.
        temp_password = 'password'
        temp_email = 'email@email.com'
        emp_group = Group.objects.get(name='Employee')
        user_params = (params.get('username'), temp_email, temp_password, )
        new_user = User.objects.create_user(*user_params)
        new_user.last_name = params.get('last_name')
        new_user.first_name = params.get('first_name')
        new_user.groups.add(emp_group)
        new_user.save()
        # create new Employee instance.
        new_emp = Employee()
        new_emp.user = new_user
        new_emp.street1 = params.get('street1')
        new_emp.street2 = params.get('street2')
        new_emp.city = params.get('city')
        new_emp.state = params.get('state')
        new_emp.zip_code = params.get('zip_code')
        new_emp.date_started = params.get('date_started')
        new_emp.starting_wage = params.get('starting_wage')
        new_emp.save()

    def edit_employee(self, attrs):
        params = attrs
        user = params.get('employee')
        last_name = params.get('last_name')
        first_name = params.get('first_name')
        username = params.get('username')
        street1 = params.get('street1')
        street2 = params.get('street2')
        city = params.get('city')
        state = params.get('state')
        zip_code = params.get('zip_code')
        date_started = params.get('date_started')
        starting_wage = params.get('starting_wage')
        current_wage = params.get('current_wage')
        # Test if any user information is changed.
        user_test = (
            last_name == user.last_name,
            first_name == user.first_name,
            username == user.username
        )
        if False not in user_test:
            # Some of the info is different, so need to update.
            user.last_name = last_name
            user.first_name = first_name
            user.username = username
            user.save()
        else:
            # No need to save. Info is all the same.
            pass
        # get correct Employee instance for the user.
        employee = Employee.objects.get(user=user)
        # Test if user's employee info has changed
        emp_test = (
            employee.street1 == street1,
            employee.street2 == street2,
            employee.city == city,
            employee.state == state,
            employee.zip_code == zip_code,
            employee.date_started == date_started,
            employee.starting_wage == starting_wage,
            employee.current_wage == current_wage
        )
        if False in emp_test:
            # Some info is different, so need to update.
            employee.street1 = street1
            employee.street2 = street2
            employee.city = city
            employee.state = state
            employee.zip_code = zip_code
            employee.date_started = date_started
            employee.starting_wage = starting_wage
            employee.current_wage = current_wage
            employee.save()
        return True


