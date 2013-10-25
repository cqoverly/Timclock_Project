from django.contrib.auth.models import User, Group, Permission

import random

#Checl for Group.Employee & Group.Manager, create if don't exist.
MANAGER = Group.objects.get_or_create(name='Manager')[0]
EMPLOYEE = Group.objects.get_or_create(name='Employee')[0]
# Check if permissions have been created.

if not EMPLOYEE.permissions.all():
    ADD_STAMP = Permission.objects.get(name='Can add Can add timestamp')
    CHANGE_STAMP = Permission.objects.get(name='Can add Can change timestamp')
    EMPLOYEE.permissions.add(ADD_STAMP)
    EMPLOYEE.permissions.add(CHANGE_STAMP)
    EMPLOYEE.save()
if not MANAGER.permissions.all():
    ADD_USER = Permission.objects.get(name='Can change user')
    MANAGER.permissions.add(ADD_USER)
    MANAGER.save()

STREET_ADDS = [
    'Farthing Ave.',
    'Wellness Pl.',
    'Chatham Way',
    'INterlake Ave.',
    '13th Ave',
    'Sanoma Pl.',
    'Barbados Way',
    'Kookoo Chichi Ave.']

DIRECTIONS = ['N.', 'S.', 'E.', 'W.', '']

F_NAMES = ['John', 'Heather', 'Andy', 'Rob', 'Vince', 'Ian', 'Julie', 'Jim']
L_NAMES = ['Winston', 'Clinton', 'Bush', 'Ford', 'Carter', 'Nixon', 'Washinton',
           'Roosevelt']


def gen_users():
    for i in range(len(F_NAMES)):
        first_name, last_name = random.choice(F_NAMES), random.choice(L_NAMES)
        F_NAMES.remove(first_name)
        L_NAMES.remove(last_name)
        username = '{}{}'.format(first_name[0], last_name).lower()
        # initials = '{}{}'.format(first_name[0], last_name[0])
        # number = random.randint(100, 8000)
        # street = random.choice(STREET_ADDS)
        # STREET_ADDS.remove(street)
        # street1 = '{} {} {}'.format(
        #     number,
        #     street,
        #     random.choice(DIRECTIONS)
        #     )
        # city = 'Seattle'
        # state = 'WA'
        # zip_code = str(random.randint(98101, 98210))
        # starting_wage = random.randint(15, 25)+(random.choice([0,5])/10.00)
        # current_wage = starting_wage + random.randint(1,4)
        # print """
        # {} {}
        # {}
        # {}
        # {}
        # {}, {}  {}
        # Startin Wage: {}  Current Wage: {}
        # """.format(
        #     first_name, last_name,
        #     username,
        #     initials,
        #     street1,
        #     city, state, zip_code,
        #     starting_wage, current_wage)

        # Employee.objects.create(
        #     first_name=first_name,
        #     last_name=last_name,
        #     username=username,
        #     initials=initials,
        #     street1=street1,
        #     city=city,
        #     state=state,
        #     zip_code=zip_code,
        #     starting_wage=starting_wage,
        #     current_wage=current_wage
        #     )

        email = '{}@timeclock.com'.format(username)
        new_user = User.objects.create_user(username=username,
            password='password',
            email='')

        new_user.last_name = last_name
        new_user.first_name = first_name
        new_user.groups.add(EMPLOYEE)
        new_user.save()




