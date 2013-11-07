# Python Std Lib modules
import datetime
from datetime import timedelta
import calendar

# 3rd Party Impots
import pytz


# django modules
import django.utils
from django.conf import settings
from django.contrib.auth.models import User

# project modules
from .models import Timestamp


TZ = pytz.timezone(settings.TIME_ZONE)
UTC = pytz.timezone('utc')
WEEKDAYS = ['Sun', 'Mon', 'Tues', 'Wed', 'Thur', 'Fri', 'Sat']
WEEKDAY_NUMBERS = [6, 0, 1, 2, 3, 4, 5, 6]
WEEKDAY_DICT = dict(zip(WEEKDAYS, WEEKDAY_NUMBERS))


def convert_timedelta(duration):
    """
    Converts a timedelta object into hours

    >>> duration = timedelta(0, 45644)
    >>> hours = convert_timedelta(duration)
    >>> print hours
    12.67

    """
    days, seconds = duration.days, duration.seconds
    hours = (seconds / 3600) + (days * 24)
    minutes = (seconds % 3600) / 60
    return round((hours + minutes/60.0), 2)


def convert_date(str_date):
    """
    Converts a string representation of a date from 5 different formats into
    datetime objects.

    Formats allowed:
        '%m/%d/%Y'
        '%m/%d/%y'
        '%Y-%m-%d'
        '%m-%d-%Y'
        '%m-%d-%y'

    >>> str_1 = '9/9/2013'
    >>> convert_date(str_1)
    datetime.datetime(2013, 9, 9, 0, 0, tzinfo=<DstTzInfo 'America/Los_Angeles' PDT-1 day, 17:00:00 DST>)
    >>> str_2 = '2/2/13'
    >>> convert_date(str_2)
    datetime.datetime(2013, 2, 2, 0, 0, tzinfo=<DstTzInfo 'America/Los_Angeles' PST-1 day, 16:00:00 STD>)
    >>> str_3 = '2013-4-5'
    >>> convert_date(str_3)
    datetime.datetime(2013, 4, 5, 0, 0, tzinfo=<DstTzInfo 'America/Los_Angeles' PDT-1 day, 17:00:00 DST>)
    >>> str_4 = '7-12-2012'
    >>> convert_date(str_4)
    datetime.datetime(2012, 7, 12, 0, 0, tzinfo=<DstTzInfo 'America/Los_Angeles' PDT-1 day, 17:00:00 DST>)
    >>> str_5 = '6-12-2012'
    >>> convert_date(str_5)
    datetime.datetime(2012, 6, 12, 0, 0, tzinfo=<DstTzInfo 'America/Los_Angeles' PDT-1 day, 17:00:00 DST>)

    """
    dtz = django.utils.timezone
    formats = ['%m/%d/%Y', '%m/%d/%y', '%Y-%m-%d', '%m-%d-%Y', '%m-%d-%y']
    d = None
    for f in formats:
        try:
            d = datetime.datetime.strptime(str_date, f)
            d_aware = dtz.make_aware(d, TZ)
            return d_aware
        except:
            pass
    raise ValueError('Invalid Format')

def get_payperiod(date):
    """
    Find the working pay period from the argument date.

    For 12th Avenue Iron, there are 2 pay periods per month:
        First through 15th
        16th through last day of month.

    >>> date = datetime.datetime(2013, 9, 9, 0, 0, tzinfo=<DstTzInfo 'America/Los_Angeles' PDT-1 day, 17:00:00 DST>)
    >>> start, end = get_payperiod(date)
    >>> print start
    datetime.datetime(2013, 9, 1, 0, 0, tzinfo=<DstTzInfo 'America/Los_Angeles' PDT-1 day, 17:00:00 DST>)
    >>> print end
    datetime.datetime(2013, 9, 16, 0, 0, tzinfo=<DstTzInfo 'America/Los_Angeles' PDT-1 day, 17:00:00 DST>)

    The returned end time will actually be the very beginning of the day
    following the last day of the period so as to encompass the full day
    of the last day of the period when querying the date range.
    """
    d = date
    period_start = None
    period_end = None
    if d.day in range(1,16):
        period_start = datetime.datetime(d.year, d.month, 1, tzinfo=TZ)
        period_end = datetime.datetime(d.year, d.month, 16, tzinfo=TZ)
    else:
        month = d.month
        year = d.year
        period_start = datetime.datetime(year, month, 16, tzinfo=TZ)
        end_year = year
        month_plusone = (month+1 if month<12 else 1)
        if month_plusone == 1:
            end_year = year + 1
        # last_day = calendar.monthrange(year, month)[1]
        period_end = datetime.datetime(end_year, month_plusone, 1, tzinfo=TZ)
    return period_start, period_end


######### MADE REDUNDANT BY get_stamplist(range)
# def get_range(employee, date_start, date_end):
#     stamps = Timestamp.objects.filter(
#         user=employee,
#         stamp__range=(date_start, date_end)
#     )
#     stamps = stamps.order_by('stamp')
#     return stamps

def get_stamplist(employee, date_range):
    if employee not in User.objects.filter(groups__name='Employee'):
        msg = "An User instance belonging to Group 'Employee' is required."
        raise TimecardError(msg)
    if type(date_range) != 'tuple' and len(date_range) != 2:
        raise TimecardError('Incorrect range input.')
    # generate list within the provided range.
    start, end = date_range[0], date_range[1] + timedelta(1)
    stamp_list = Timestamp.objects.filter(user=employee,
                                          stamp__range=(start, end))

    # TODO: code to verify in_out correctness and msg if edits needed.
    return stamp_list


class Timecard():
    """
    Timecard(employee, date)

    ============ ARGS =============
    employee and date are required.

    employee:   User instance belonging to the custom User group "Employee"

    date:       A string representation of a date which must use one of the
                following formats:
                    '%m/%d/%Y'
                    '%m/%d/%y'
                    '%Y-%m-%d'
                    '%m-%d-%Y'
                    '%m-%d-%y'


    ============= DESCRIPTION ===========
    A Timecard instance is created based on an Employee instance and a
    string formatted date. Calculations determine what hours from the
    previous pay period are applicable for overtime, total regular hours,
    total overtime (OT) hours. A csv file is produced representing all
    hours worked.

    The primary attribute in a Timecard instance is the ._card attribute. The
    ._card attribute is  dict of containing:
            -   Pairs of in and out Timestamp instances for each week in the
                pay period.
            -   Regular_Hours
            -   OT_Hours
            -   Total_Hours
    """
    def __init__(self, user, date):
        """
        - employee is any instance of employee_manager.models.Employee
        - date is any date within the pay period being calculated.
        - date is used to determine the period start_date, end_date
          and start_weekday.
        """
        self.req_date = convert_date(date)
        self.emp = user
        self.start_date, self.end_date = get_payperiod(self.req_date)
        self.start_weekday = self.start_date.weekday()
        self._card = self._get_card()
        self.total_hrs, self.regular_hrs, self.OT_hrs = self._add_hours()

    @property
    def _OTweek_start(self):
        """
        calculates the beginning of the workweek used for calculating
        overtime, which is based on a Sunday to Saturday system.
        """
        if self.start_weekday == 6:
        # Period start day is a Sunday
            return self.start_date
        else:
        # Period start_date is not a Sunday
            # Get how many days back is a Sunday which is the start day
            # for OT calculations
            diff = timedelta(self.start_weekday+1)
            # subtract days back to get date of OT start and return
            return self.start_date - diff

    @property
    def _stamps(self):
        """
        Collects all timestamps for the Timecard instance's employee for the
        instance's time period.
        """
        all_stamps = Timestamp.objects.filter(
            user=self.emp,
            stamp__range=(self.start_date, self.end_date)
            ).order_by('stamp')
        if all_stamps:
            # Timestamps exist matching query
            return all_stamps
        else:
            # No Timestamps matched query.
            raise ValueError('No stamps for requested time period.')

    def __str__(self):
        return """
        {}:  {}
        {}:  {}
        {}:  {}
        {}:  {}
        {}:  {}
        {}:  {}
        {}:  {}
        """.format(
            'Employee', self.emp,
            'Timecard Start Date', self.start_date,
            'Timecard End Date', self.end_date,
            'Start of Week for OT Calculation', self._OTweek_start,
            'Total Hours', self.total_hrs,
            'Regular Hours', self.regular_hrs,
            'Overtime Hours', self.OT_hrs
            )

    # @property
    def _get_card(self):
        """
        Creates a timecard for the instance's date range.
        Makes a call to validate_card to check for errors.
        Sends notification on failure, calls calculate_hours if
        successful.
        """
        try:
        # Generate list of IN/OUT two-tuples
            inout_pairs = self._generate_pairs(self._stamps)
            #check to make sure pairings are valid.
            self._verify_pairs(inout_pairs) # throws ValueError if not valid
            # get hours from previous period to be used in OT computation.
            prevOT_hours = self._previousOT()
            # divide list of pay period stamps into weeks
            weeks_dict = self._split_weeks(inout_pairs)
            # Calculate total hours for each week.
            for week in weeks_dict:
                week_stamps = weeks_dict[week]['stamps']
                week_total = sum([s[2] for s in week_stamps])
                if week == 'week1':
                    reg_hrs = week_total - prevOT_hours
                    weeks_dict[week]['Regular_Hours'] = reg_hrs
                    weeks_dict[week]['OT_Hours'] = prevOT_hours
                    weeks_dict[week]['Total_Hours'] = week_total
                else:
                    OT_hours = max([week_total - 40, 0])
                    reg_hrs = week_total - OT_hours
                    weeks_dict[week]['Regular_Hours'] = reg_hrs
                    weeks_dict[week]['OT_Hours'] = OT_hours
                    weeks_dict[week]['Total_Hours'] = week_total
            return weeks_dict
        except ValueError, e:
            # Catches exception thrown in _verify_pairs, and passes it through.
            raise ValueError(e)

    def _generate_pairs(self, timestamps):
        """
        _generate_pairs creates a list of tuples from all Timestamp
        instances for the employee within the start_date and end_date
        range:
            pair = (stamp1, stamp2, hours)

        stamp1 and stamp2 are Timestamp instances.
        hours is a return from timeclock.convert_timedelta. It provides
        the difference between the two Timestamp.stamp values in hours.
        """
        stamps = timestamps
        stamp_pairs = []
        r = range(0, len(stamps), 2)
        for i in r:
            s1, s2 = stamps[i], stamps[i+1]
            stamp_pairs.append((s1, s2, convert_timedelta(s2.stamp-s1.stamp)))
        return stamp_pairs

    def _verify_pairs(self, stamp_tuples):
        """
        Takes a list of tuples with following values:
            (stamp1, stamp2, hours)

        stamp1 and stamp2 are instances of class Timestamp, each with
        and in_out value of either 'IN' or 'OUT'. Each tuple is checked to
        ensure 'IN' is the value of the
        """
        stamps = self._stamps
        if not stamps:
            template = "No timestamps for dates: {} to {}."
            start = self.start_date.strftime('%m/%d/%Y')
            end = self.end_date.strftime('%m/%d/%Y')
            error_msg = template.format(start, end)
            raise IndexError(error_msg)
        elif stamps[0].in_out != 'IN':
            raise TimecardError("First stamp is 'Out', should be 'IN'")
        for i in range(0, len(stamps), 2):
            s1, s2 = stamps[i], stamps[i+1]
            if s1.in_out != 'IN' or s2.in_out != 'OUT' or s1.stamp >= s2.stamp:
                raise TimecardError('Stamps out of order')
        return True

    def _previousOT(self):
        """
        Calculates the hours of overtime in the first full week of timeperiod.
        Even thought the pay period may not start on Sunday, for OT purposes
        anything over 40 hours in a Sunday to Saturday period is considered
        overtime and can often only be calculate once the week is complete.
        """
        # Range of the workweek for OT purposes.
        r = (self._OTweek_start, self._OTweek_start+timedelta(7))
        full_week1 = Timestamp.objects.all().filter(user=self.emp,
            stamp__range=(r)).order_by('stamp')
        self._verify_pairs(full_week1)
        inout_pairs = self._generate_pairs(full_week1)
        full_hours = sum([s[2] for s in inout_pairs])
        OThours = full_hours - 40
        return max([OThours, 0])

    def _split_weeks(self, pairs):
        """
        Splits the full list of in/out pairs into a list of lists
        based on workweeks, a workweek being from Sunday(6) - Saturday(5)
        """
        wk1_start = self._OTweek_start
        wk2_start = wk1_start + timedelta(7)
        wk3_start = wk1_start + timedelta(14)
        wk3_end = self.end_date
        # Break up the stamp_pairs into lists of workweek periods.
        wk1 = [p for p in pairs if p[0].stamp >= wk1_start and p[1].stamp < wk2_start]
        wk2 = [p for p in pairs if p[0].stamp >= wk2_start and p[1].stamp < wk3_start]
        wk3 = [p for p in pairs if p[0].stamp >= wk3_start and p[1].stamp < wk3_end]
        if wk3:
            return dict(zip(['week1', 'week2', 'week3'],
                [{'stamps': wk1}, {'stamps':wk2}, {'stamps': wk3}]))
        else:
            return dict(zip(['week1', 'week2'],
                [{'stamps': wk1}, {'stamps':wk2}]))

    def _add_hours(self):
        """
        Calculates the total hours from each week in the self_card
        property to provide the total hours worked in the pay period
        range.

        The values are then added as dict keys in the self._card attribute,
        which are then passed to the following Timecard attributes:
                self.total_hrs
                self.regular_hrs
                self.OT_hrs
        """
        total_hours = 0
        regular_hours = 0
        OT_hours = 0
        for w in self._card:
            total_hours += self._card[w]['Total_Hours']
            regular_hours += self._card[w]['Regular_Hours']
            OT_hours += self._card[w]['OT_Hours']
        return (
            round(total_hours, 2),
            round(regular_hours, 2),
            round(OT_hours, 2)
            )


class TimecardError(Exception):
    """
    Custom exception for errors generating a Timecard instance.
    """
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        base_str = "There was an error generating you timecard:"
        full_str = "{0}\n{1}".format(base_str, self.msg)
        return full_str

class TimestampEntryError(Exception):
    """
    Custom exception for generating Timestamp instance.
    """
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        base_str =  "There was an error generating the timestamp:"
        full_str = "{}\n{}".format(base_str, self.msg)
        return full_str

