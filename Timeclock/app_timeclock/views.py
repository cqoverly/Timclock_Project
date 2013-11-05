# Python Std Lib modules
import datetime

# 3rd Party modules
import pytz

# django modules
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User, Group


# project modules
from Timeclock import settings

from .forms import (
    TimestampForm,
    EmpViewTimecardForm,
    ManagerViewTimecardForm,
    EditStampForm,
)
from .models import Timestamp, TimestampEdits
from .functions_classes import Timecard


TZ = pytz.timezone(settings.TIME_ZONE)

def vw_punch_clock(request):
    employee = request.user
    if request.method == 'POST':
        form = TimestampForm(request.POST)
        if request.POST.get('cancel') == '':
                return redirect('home')
        elif form.is_valid():
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

    in_out = Timestamp.set_inout(employee)
    params = {
        'stamp': datetime.datetime.now().strftime('%m/%d/%Y  %H:%M'),
        'in_out':in_out
    }
    form = TimestampForm(initial=params)
    return render(request, 'punch_clock.html', {'form':form})


def vw_view_timecard(request):
    print 'In vw_view_timecard'
    # Assumed user is an Employee
    TimecardForm = EmpViewTimecardForm
    user_isemployee = True
    user = request.user
    #if user is in Manager User Group, switch form type
    if user not in User.objects.filter(groups__name='Employee'):
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
                templ = '%m/%d/%y' # used to reformat date for Timecard.__init__
                str_date = date.strftime(templ)

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
    except ValueError, e:
        msg = '{}: {}'.format('ValueError', e)
        messages.add_message(request, messages.ERROR, msg)

    # employee = request.user
    form = TimecardForm()
    return render(request, 'view_timecard.html', {'form': form})

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
            stamps or delayed stamps as workers do not always have access to the
            timeclock, or just forget.
    """
    user = request.user
    orig_stamp = Timestamp.objects.get(pk=pk)
    if request.method == 'POST':
        form = EditStampForm(request.POST)
        if request.POST.get('cancel') == '':
            return redirect('home')
        elif form.is_valid():
            new_datetime = form.cleaned_data['new_datetime']
            new_inout = form.cleaned_data['new_inout']
            editable_params = {
                'timestamp': orig_stamp,
                'changed_by': user,
                'for_employee': orig_stamp.user,
                'original_datetime': orig_stamp.stamp,
                'original_inout': orig_stamp.in_out,
                'new_datetime': new_datetime,
                'new_inout': new_inout,
                'change_reason': form.cleaned_data['change_reason'],
                'date_changed': datetime.datetime.now(),
            }
            #### Is this necessary?
            update_params = {
                'stamp': new_datetime,
                'in_out': new_inout,
            }
            ####
            # Update stamp fields
            orig_stamp.stamp = new_datetime
            orig_stamp.in_out = new_inout
            edit_entry = TimestampEdits(**editable_params)

            # Update stamp
            orig_stamp.save()
            # create new record in EditStamp table
            edit_entry.save()
            msg = "Your timestamp has been changed."
            messages.add_message(request, messages.SUCCESS, msg)
            return redirect('home')
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









