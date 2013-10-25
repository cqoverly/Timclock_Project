from django.utils import timezone
import pytz
from models import Timestamp as TS
from datetime import datetime, timedelta
import random

from django.contrib.auth.models import User, Group
from Timeclock import settings
from .models import Timestamp

pac_tz = pytz.timezone(settings.TIME_ZONE)

def generate_stamps(employee):
    stamp_times = [
                datetime(2013, 9, 15, 7, 45),
                datetime(2013, 9, 15, 12, 13),
                datetime(2013, 9, 15, 12, 45),
                datetime(2013, 9, 15, 16, 42),
                datetime(2013, 9, 16, 7, 55),
                datetime(2013, 9, 16, 11, 59),
                datetime(2013, 9, 16, 12, 32),
                datetime(2013, 9, 16, 17, 22),
                datetime(2013, 9, 17, 7, 55),
                datetime(2013, 9, 17, 12, 05),
                datetime(2013, 9, 17, 12, 27),
                datetime(2013, 9, 17, 18, 03),
                datetime(2013, 9, 18, 7, 55),
                datetime(2013, 9, 18, 11, 59),
                datetime(2013, 9, 18, 12, 27),
                datetime(2013, 9, 18, 16, 32),
                datetime(2013, 9, 19, 8, 00),
                datetime(2013, 9, 19, 12, 32),
                datetime(2013, 9, 19, 13, 03),
                datetime(2013, 9, 19, 16, 55),
                datetime(2013, 9, 20, 7, 35),
                datetime(2013, 9, 20, 11, 46),
                datetime(2013, 9, 20, 12, 13),
                datetime(2013, 9, 20, 17, 13),
                datetime(2013, 9, 23, 7, 56),
                datetime(2013, 9, 23, 16, 01),
                datetime(2013, 9, 24, 7, 30),
                datetime(2013, 9, 24, 11, 55),
                datetime(2013, 9, 24, 12, 20),
                datetime(2013, 9, 24, 17, 33),
                datetime(2013, 9, 25, 8, 01),
                datetime(2013, 9, 25, 11, 55),
                datetime(2013, 9, 25, 12, 23),
                datetime(2013, 9, 25, 16, 57),
                datetime(2013, 9, 26, 7, 31),
                datetime(2013, 9, 26, 16, 57),
                datetime(2013, 9, 27, 7, 32),
                datetime(2013, 9, 27, 11, 31),
                datetime(2013, 9, 27, 11, 54),
                datetime(2013, 9, 27, 16, 32),
                datetime(2013, 9, 30, 7, 43),
                datetime(2013, 9, 30, 12, 02),
                datetime(2013, 9, 30, 12, 45),
                datetime(2013, 9, 30, 17, 32),
                ]

    i_o = 'OUT'

    for s in stamp_times:
        delta = timedelta(minutes=random.randint(-5, 5))
        if i_o == 'IN':
            i_o = 'OUT'
        else:
            i_o = 'IN'#gen
        new_s = timezone.make_aware(s+delta, pac_tz)
        ts = TS(employee=employee, stamp=new_s, in_out=i_o)
        ts.save()

def stamps_forall():
    EMPLOYEE = Group.objects.get_or_create(name='Employee')[0]
    emps = User.objects.all()
    for e in emps:
        if EMPLOYEE in e.groups.all():
            make_stamps(e)
            total = len(Timestamp.objects.all().filter(user=e))
            print '{} stamps created for {}'.format(total, e)



def make_stamps(emp):
    START_DATE = datetime(2010, 1, 1).date()
    END_DATE = datetime.now().date()
    delta = timedelta(1)
    temp_date = START_DATE
    dates = []
    while temp_date <= END_DATE:
        if temp_date.weekday() not in (6, 7):
            dates.append(temp_date)
        else:
            if random.randint(1, 20) == 5:
                dates.append(temp_date)
        temp_date += delta
    stamps = []
    user = emp
    # create in/out stamps for each day
    for d in dates:
        if not random.randint(1, 100) == 50: # if not a sick day
        # create in/out stamps for specic date
            day_stamps = create_day(d)
            for stamp in day_stamps:
                new_stamp = Timestamp(user=user,
                    stamp=stamp[0],
                    in_out=stamp[1])
                new_stamp.save()

    return stamps


def create_day(date):
    aware_stamp = lambda s: timezone.make_aware(s, pac_tz)
    # get values for times
    Y = date.year
    m = date.month
    d = date.day
    # morning clock in
    in_mornhour = random.randint(6,8)
    in_mornmin = random.randint(1, 59)
    stamp = datetime(Y, m, d, in_mornhour, in_mornmin)
    morn_stamp = aware_stamp(stamp)
    morn_in = (morn_stamp, 'IN')
    #lunch clock out
    out_lunchhour = random.randint(11, 12)
    out_lunchmin = random.randint(1, 59)
    stamp = datetime(Y, m, d, out_lunchhour, out_lunchmin)
    outlunch_stamp = aware_stamp(stamp)
    lunch_out = (outlunch_stamp, 'OUT')
    #lunch clock in
    lunch_length = timedelta(minutes=random.randint(20, 45))
    inlunch_stamp = lunch_out[0] + lunch_length
    # inlunch_stamp = aware_stamp(stamp)
    # print 'InLunch post aware: {}'.format(inlunch_stamp)
    lunch_in = (inlunch_stamp, 'IN')
    # evening clock out
    out_evehour = random.randint(16, 19)
    out_evemin = random.randint(1, 59)
    stamp = datetime(Y, m, d, out_evehour, out_evemin)
    eve_stamp = aware_stamp(stamp)
    eve_out = (eve_stamp, 'OUT')
    return (morn_in, lunch_out, lunch_in, eve_out)


