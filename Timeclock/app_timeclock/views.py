# Python Std Lib modules
import datetime
from datetime import timedelta

# 3rd Party modules
import pytz

# django modules
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required


# project modules
from django.conf import settings
from .functions_classes import (
    TimecardError,
    TimestampEntryError,
    get_stamplist
)
from .forms import (
    TimestampForm,
    EmpViewTimecardForm,
    ManagerViewTimecardForm,
    EditStampForm,
    MgrViewTimestampListForm,
    EmpViewTimestampListForm
)
from .models import Timestamp, TimestampEdits
from .functions_classes import Timecard


TZ = pytz.timezone(settings.TIME_ZONE)


@login_required
def vw_punch_clock(request):
    employee = request.user
    if request.method == 'POST':
        form = TimestampForm(request.POST)
        if request.POST.get('cancel') == '':
                return redirect('home')
        elif form.is_valid():
            try:
                # employee = Employee.objects.get(username=request.user.username)
                stamp_dt = form.cleaned_data['stamp']
                in_out = form.cleaned_data['in_out']
                #convert aware datetime
                stamp = stamp_dt
                params = {'user': employee,
                    'stamp': stamp,
                    'in_out': in_out
                    }
                timestamp = Timestamp(**params)
                timestamp.save()
                msg = 'You have been clocked {} @ {}'.format(in_out, stamp)
                messages.add_message(request, messages.SUCCESS, msg)
                return redirect('home')
            except TimestampEntryError, e:
                msg = """
                {}\n Please review your card and correct.
                """.format(e)
                params = {'stamp': stamp_dt, 'in_out': in_out}
                form = TimestampForm(initial=params)
                messages.add_message(request, messages.ERROR, msg)
                return render(request, 'punch_clock.html', {'form': form})

    in_out = Timestamp.set_inout(employee)
    params = {
        'stamp': datetime.datetime.now().strftime('%m/%d/%Y  %H:%M'),
        'in_out':in_out
    }
    form = TimestampForm(initial=params)
    return render(request, 'punch_clock.html', {'form': form})


@login_required
def vw_view_timecard(request):
    """
    Displays form for selecting a pay period to display, then displays a
    Timecard instance for that pay period.

    Form provided depends on whether the request.user is a manager or employee,
    the former presented with the ability to choose any employee to view. An
    employee is only allowed to view their own timecard.

    The information is retrieved through creation of a Timecard instance and
    its methods.

    """
    # Assumed user is an Employee
    TimecardForm = EmpViewTimecardForm
    user_isemployee = True
    user = request.user
    #if user is in Manager User Group, switch form type
    if user in User.objects.filter(groups__name='Manager') or user.is_superuser:
        TimecardForm = ManagerViewTimecardForm
        user_isemployee = False
    try:
        if request.method == 'POST':
            form = TimecardForm(request.POST)
            employee = None
            if request.POST.get('cancel') == '':
                # cancel timecard lookup
                return redirect('home')
            elif form.is_valid():

                # TODO: Can Timecard display params be passed from a Timecard method?
                # timecard lookup requested/
                if user_isemployee:
                    # user viewing EmpViewTimecardForm, has no employee field
                    employee = user
                else:
                    # user viewing ManagerViewTiemcardForm, has list of emps.
                    employee = form.cleaned_data['name']
                date = form.cleaned_data['date']    #date within timecard period
                                                    # desired.
                # reformat date to pass into Timecard.__init__
                templ = '%m/%d/%y' # used to format date for Timecard.__init__
                str_date = date.strftime(templ)
                # generate a Timecard instance.
                timecard = Timecard(employee, str_date)
                card = timecard._card.items()   # create list of dicts to sort
                card.sort()                     # by week
                # create form to send to view_timecard.html along with data
                # to allow user to edit and resend the form if needed.
                initial = None
                if user_isemployee:
                    initial = {'date': str_date}
                else:
                    initial = {'name':employee, 'date': str_date}
                form = TimecardForm(initial=initial)
                # set parameters to send to view_timecard.html
                regular_hrs = timecard.regular_hrs
                OT_hrs = timecard.OT_hrs
                total_hrs = timecard.total_hrs
                params = {
                    'form':form,
                    'card': card, # sorted list of dicts with 'week' keys
                    'regular_hrs': regular_hrs,
                    'OT_hrs': OT_hrs,
                    'total_hrs': total_hrs
                }
                return render(request,
                    'view_timecard.html',
                    params
                    )
    except IndexError, e:
        msg = '{}: {}'.format('IndexError', e)
        messages.add_message(request, messages.ERROR, msg)
    except TimecardError, e:
        msg = '{}: {}'.format('ValueError', e)
        messages.add_message(request, messages.ERROR, msg)

    # employee = request.user
    form = TimecardForm()
    return render(request, 'view_timecard.html', {'form': form})


@login_required
def vw_edit_timestamp(request, pk):
    """
    View processes a request to change an existing Timestamp instance.
    Two primary actions occur upon successful POST:
        1) The instance is updated with the new data.
            This update involves checking to make sure the date fits within
            the current Timestamp order for the particular employee. It is
            essential that stamps are not allowed to occur out of order as this
            will create an inability to create a correct Timecard.
        2) A new record is created in the app_timeclock_timestampedits table.
            The primary purpose of this record is for management to monitor
            changes, as the employees themselves are allowed to make the
            updates. This is neccessary to keep managers from constantly having
            to fix the stamps on their own. Clock punching is rife with missed
            stamps or delayed stamps as workers do not always have access to
            the timeclock or forget to punch the clock.
    """
    user = request.user
    orig_stamp = Timestamp.objects.get(pk=pk)
    try:
        if request.method == 'POST':
            form = EditStampForm(request.POST, orig_stamp=orig_stamp)
            print request.POST
            if request.POST.get('cancel') == '':
                return redirect('home')
            elif form.is_valid():
                new_datetime = form.cleaned_data['new_datetime']
                new_inout = form.cleaned_data['new_inout']
                reason = form.cleaned_data['change_reason']
                print "HERE 1"
                orig_stamp.edit_timestamp(
                    request.user,
                    new_datetime,
                    new_inout,
                    reason)
                print "HERE 2"
                msg = "Your timestamp has been changed."
                messages.add_message(request, messages.SUCCESS, msg)
                return redirect('home')
    except TimestampEntryError, e:
            print "HERE# 3"
            msg = """
            {}\n Please review and correct your previous time stamps.
            """.format(e)
            messages.add_message(request, messages.ERROR, msg)
    # generate initial form with date from stamp to be changed for convenience.
    initial_params = {
        'new_datetime': orig_stamp.stamp,
        'new_inout': orig_stamp.in_out,
    }
    form = EditStampForm(initial=initial_params)
    return render(
        request,
        'edit_stamp.html',
        {'form': form,
        'stamp': orig_stamp, # sent along to use attributes in page.
        }
    )

# TODO: Test for error handling.
# TODO: Add docstring and line commnets
@login_required
def vw_list_timestamps(request):
    """
    The vw_list_timestamps view generates a form to select a date range from
    which to generate of list of timestamps for a particular User. If the
    request.user is belongs to the Manager group, then the form will have a
    select widget containg a list of all Users belonging to the Employee group.
    If the User is not a memeber of the Manager group, then just the text fields
    for a date are displayed, and the request.user become the employee for the
    query search when the form is submitted.

    Upon a successful submit, the list of timesetamps is generated and a page
    is rendered with the list and date parameters passed to the page to be used
    if desired, along with a form instance.
    """
    is_manager = False
    form = None
    # page_form = None
    # Determine if user is manager
    if request.user in User.objects.filter(groups__name="Manager")\
        or request.user.is_superuser:
        is_manager = True
        print 'IS MANAGER'
        page_form = MgrViewTimestampListForm
    else:
        page_form = EmpViewTimestampListForm

    if request.method == 'POST':
        # Determine correct form to use.
        if is_manager:
            form = page_form(request.POST)
        else:
            form = page_form(request.POST)
        if request.POST.get('cancel') == '':
            return redirect('home')
        elif form.is_valid():
            if is_manager:
                # if it is the manager form, employee name needs to be pulled.
                employee = form.cleaned_data['employee']
            else:
                # if it's the employee form, employee is the request.user
                employee = request.user
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            # create tuple from dates to send to get_stamplist(employee, range)
            date_range = (start_date, end_date)
            # generate list of stamps.
            stamps = get_stamplist(employee, date_range)
            return render(
                request,
                'view_stamplist.html',
                {'form': form,
                 'stamps': stamps,
                 'start': start_date,
                 'end': end_date + timedelta(1),
                 'employee': employee
                 }
            )

    form = page_form()
    return render(
        request,
        'view_stamplist.html',
        {'form': form}
    )






