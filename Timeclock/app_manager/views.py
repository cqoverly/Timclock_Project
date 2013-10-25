# Python Std Library Imports

# Django Frameword Imports
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView
from django.contrib import messages
from django.db import IntegrityError
from django.forms import ValidationError

# Third Part Imports

# Timeclock App Imports
from .forms import AddEmployeeForm, ChangePasswordForm
from .models import Employee

# def vw_view_employees(request):
#     return render(request, 'view-employees.html')

class EmployeeList(ListView):
    model = User
    template_name = 'employee_list.html'
    employees = User.objects.filter(groups__name='Employee')
    queryset = employees.order_by('last_name', 'first_name')

class EmployeeDetail(DetailView):
    model = User
    context_object_name = 'employee'
    template_name = 'employee_detail.html'

def vw_employee_detail(request, username):
    employee = User.objects.get(username=username)
    return render(request, 'employee_detail.html', {'employee': employee})


# def vw_edit_employee(request, pk):
#     employee = User.objects.get(pk=pk)
#     if request.method == 'POST':
#         form = AddEmployeeForm(request.POST)
#         if request.POST.get('cancel') == '':
#             return redirect('home')
#         elif form.is_valid():
#             last_name = form.cleaned_data['last_name']
#             first_name = form.cleaned_data['first_name']
#             username = form.cleaned_data['username']
#             initials = form.cleaned_data['initials']
#             street1 = form.cleaned_data['street1']
#             street2 = form.cleaned_data['street2']
#             city = form.cleaned_data['city']
#             state = form.cleaned_data['state']
#             zip_code = form.cleaned_data['zip_code']
#             date_started = form.cleaned_data['date_started']
#             starting_wage = form.cleaned_data['starting_wage']
#             # Update Employee instance.
#             params = {
#                 'last_name': last_name,
#                 'first_name': first_name,
#                 'username': username,
#                 'initials': initials,
#                 'street1': street1,
#                 'street2': street2,
#                 'city': city,
#                 'state': state,
#                 'zip_code': zip_code,
#                 'date_started': date_started,
#                 'starting_wage': starting_wage
#             }
#             # Save updated info
#             result = employee.edit_employee(params)
#             if result:
#                 template = "{} {}'s information has been updated."
#                 msg = template.format(employee.first_name, employee.last_name)
#                 messages.add_message(request, messages.SUCCESS, msg)
#                 return redirect('home')

#     form = AddEmployeeForm(initial=employee.__dict__)
#     return render(request, 'add_employee.html', {'form': form})

def vw_add_employee(request):
    entered_by = '' #TODO Is this a relic?
    user = request.user
    print user
    if request.method == 'POST':
        form = AddEmployeeForm(request.POST)

        if request.POST.get('cancel') == '':
            return redirect('home')
        if form.is_valid():
            last_name = form.cleaned_data['last_name']
            first_name = form.cleaned_data['first_name']
            username = form.cleaned_data['username']
            initials = form.cleaned_data['initials']
            street1 = form.cleaned_data['street1']
            street2 = form.cleaned_data['street2']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            zip_code = form.cleaned_data['zip_code']
            date_started = form.cleaned_data['date_started']
            starting_wage = form.cleaned_data['starting_wage']
            #create a new employee and user
            params = {
                'last_name': last_name,
                'first_name': first_name,
                'username': username,
                'initials': initials,
                'street1': street1,
                'street2': street2,
                'city': city,
                'state': state,
                'zip_code': zip_code,
                'date_started': date_started,
                'starting_wage': starting_wage
            }
            Employee.add_employee(params)

            form = form
            text = "{} {} has been addes as an employee w/ default password: {}"
            msg = text.format(first_name, last_name, "'password'")
            messages.add_message(request, messages.SUCCESS, msg)
            return redirect('home')
        else:
            # params = {
            #     'last_name': request.Post.get('last_name'),
            #     'first_name': request.Post.get('first_name'),
            #     'username': request.Post.get('username'),
            #     'initials': request.Post.get('initials'),
            #     'street1': request.Post.get('street1'),
            #     'street2': request.Post.get('street2'),
            #     'city': request.Post.get('city'),
            #     'state': request.Post.get('state'),
            #     'zip_code': request.Post.get('zip_code'),
            #     'date_started': request.Post.get('date_started'),
            #     'starting_wage': request.Post.get('starting_wage')
            # }
            print request.POST
            msg = 'Invalid Entries'
            messages.add_message(request, messages.ERROR, msg,
                extra_tags='warning'
            )
            form = AddEmployeeForm()
            # form = AddEmployeeForm(initial=params)
            return render(request, 'add_employee.html', {'form': form})

    form = AddEmployeeForm()
    return render(request, 'add_employee.html', {'form': form})

def vw_change_password(request):
    employee = request.user
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        try:
            if request.POST.get('cancel') == '':
                return redirect('home')
            elif form.is_valid():
                new_pw = form.cleaned_data['new_password']
                employee.set_password(new_pw)
                employee.save()
                msg = "Password successfully changed."
                messages.add_message(request, messages.SUCCESS, msg)
                return redirect('home')
        except ValueError, e:
            print 'ValidationError: {}'.format(e)
            msg = e
            messages.add_message(request,
                messages.ERROR,
                msg, extra_tags='danger')
        except AttributeError, e:
            msg = e
            messages.add_message(request,
                messages.ERROR,
                msg, extra_tags='danger')
    form = ChangePasswordForm()
    return render(request, 'change_password.html', {'form': form})

def vw_login(request):
    username = None
    if request.method == 'POST':
        if request.POST.get('cancel') == '':
            return redirect('home')
        elif request.POST.get('username') and request.POST.get('password'):
            username = request.POST.get('username')
            password = request.POST.get('password')
            try:
                user = authenticate(username=username, password=password)
                login(request, user)
                msg = "Welcome, {} {}".format(user.first_name, user.last_name)
                messages.add_message(request, messages.SUCCESS, msg)
                return redirect('home')
            except AttributeError:
                msg = "Your username and/or your password were incorrect."
                messages.add_message(request, messages.ERROR, msg,
                    extra_tags='danger'
                )
                return render(request,
                    'login.html',
                    {'username': username,
                     'password': password
                     }
                )
    return render(request, 'login.html', {'username': username})

def vw_home(request):
    # return render(request, 'home.html')

    # Test if Group obbjects have been created in the auth database.
    # Create if necessary.
    mgr = Group.objects.get_or_create(name='Manager')[0]
    emp = Group.objects.get_or_create(name='Employee')[0]

    if request.user.is_authenticated():
        user = request.user
        if mgr in user.groups.all() or request.user.is_superuser:
            return render(request,'manager_home.html')
        elif emp in user.groups.all():
            return render(request,'employee_home.html')
    return render(request, 'home.html')

def vw_manager_home(request):
    return render(request, 'manager_home.html')

def vw_employee_home(request):
    return render(request, 'employee_home.html')

def vw_employees(request):
    return render(request, 'view_employees.html')

def vw_employee(request):
    return render(request, 'view_employee.html')


