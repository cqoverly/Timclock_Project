# Python Std Lib modules
import datetime
from datetime import timedelta
import calendar

# 3rd Party Impots
import pytz

# django modules
import django.utils
from Timeclock.settings import TIME_ZONE

# project modules
from .models import Timestamp


TZ = pytz.timezone(TIME_ZONE)
UTC = pytz.timezone('utc')
WEEKDAYS = ['Sun', 'Mon', 'Tues', 'Wed', 'Thur', 'Fri', 'Sat']
WEEKDAY_NUMBERS = [6, 0, 1, 2, 3, 4, 5, 6]
WEEKDAY_DICT = dict(zip(WEEKDAYS, WEEKDAY_NUMBERS))


def convert_timedelta(duration):
    days, seconds = duration.days, duration.seconds
    hours = seconds / 3600
    minutes = (seconds % 3600) / 60
    return round((hours + minutes/60.0), 2)


def convert_date(str_date):
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


class Timecard():
    """
    Timecard(employee, date)

    employee and date are required.

    A Timecard instance is created based on an Employee instance and a
    string formatted date. Calculations determine what hours from the
    previous pay period are applicable for overtime, total regular hours,
    total overtime (OT) hours. A csv file is produced representing all
    hours worked.

    """
    def __init__(self, employee, date):
        """
        - employee is any instance of employee_manager.models.Employee
        - date is any date within the pay period being calculated.
        - date is used to determine the period start_date, end_date
          and start_weekday.
        """
        req_date = convert_date(date)
        self.emp = employee
        self.start_date, self.end_date = get_payperiod(req_date)
        self.start_weekday = self.start_date.weekday()
        print "About to get card."
        print self.emp
        self._card = self._get_card()
        self.total_hrs, self.regular_hrs, self.OT_hrs = self._add_hours()

    @property
    def _OTweek_start(self):
        """
        calculates the beginning of the workweek used for calculating
        overtime, which is based on a Sunday to Saturday system.
        """
        if self.start_weekday == 6:
            return self.start_date
        diff = timedelta(-1*(self.start_weekday+1))
        return self.start_date + diff

    @property
    def _stamps(self):
        """
        Collects all timestamps for the Timecard instance's employee for the
        instance's time period.
        """
        all_stamps = Timestamp.objects.all().filter(
            employee=self.emp,
            stamp__range=(self.start_date, self.end_date)
            ).order_by('stamp')
        # local_stamp = lambda d: d.astimezone(TZ)
        # local_stamps = [local_stamp(s) for s in all_stamps]
        # return local_stamps
        if all_stamps:
            return all_stamps
        else:
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
        Makes a call too validate_card to check for errors.
        Sends notification on failure, calls calculate_hours if
        successful.
        """
        print 'Starting _card'
        # prev_OTHours = 0
        try:
        #     first_weekHRS = 0
        #     OT_hours = 0
        #     regular_hours = 0

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
            raise ValueError("First stamp is 'Out', should be 'IN'")
        for i in range(0, len(stamps), 2):
            s1, s2 = stamps[i], stamps[i+1]
            if s1.in_out != 'IN' or s2.in_out != 'OUT' or s1.stamp >= s2.stamp:
                raise ValueError('Stamps out of order')
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
        full_week1 = Timestamp.objects.all().filter(employee=self.emp,
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

        The values are then added as dict keys in the self_card property,
        which are then passed to the following Timecard attribute:
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