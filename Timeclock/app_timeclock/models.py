# Python std library imports
import datetime

# Django framework imports
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings

# 3rd party imports
import pytz

# Project imports
# from .functions_classes import TimestampEntryError

T_ZONE = pytz.timezone(settings.TIME_ZONE)

class Timestamp(models.Model):
    TIME_IN = 'IN'
    TIME_OUT = 'OUT'
    IN_OUT_CHOICES = (
        (TIME_IN, 'In'),
        (TIME_OUT, 'Out'),
    )
    user = models.ForeignKey(User)
    stamp = models.DateTimeField()
    in_out = models.CharField(max_length=3,
        choices = IN_OUT_CHOICES,
    )

    def __str__(self):
        u = None
        if self.user.last_name:
            u = self.user.last_name
        else:
            u = self.user.username
        d = self.stamp.strftime('%m/%d/%Y')
        return '{0}  {1}  {2}'.format(u, d, self.in_out)

    @staticmethod
    def set_inout(user):
        """
        Determines whether particular employee last clocked in or
        clocked out, and returns the opposite as recommendation for
        next Timestamp.
        """
        user = user
        # if not Timestamp.objects.all().filter(user=user):
        #     return 'IN'

        # Determine state of last clock even and return opposite.
        try:
            last_stamp = Timestamp.objects.all().filter(user=user).latest('stamp')
        except Timestamp.DoesNotExist:
            # Most likely because new employee clocking in for first time.
            return 'IN'
        if last_stamp.in_out == 'IN':
            return 'OUT'
        elif last_stamp.in_out == 'OUT':
            return 'IN'
        # If all else fails
        else:
            raise AttributeError

    def edit_timestamp(self, request_user, new_dt, new_inout, reason):
        edittable_params = {
            'timestamp': self,
            'changed_by': request_user,
            'for_employee': self.user,
            'original_datetime': self.stamp,
            'original_inout': self.in_out,
            'new_datetime': new_dt,
            'new_inout': new_inout,
            'change_reason': reason,
            'date_changed': timezone.now(),
        }
        self.stamp = new_dt
        self.in_out = new_inout
        edit_entry = TimestampEdits(**edittable_params)

        # Update stamp
        self.save()
        # create new record in EditStamp table
        edit_entry.save()
        return True

    def save(self, *args, **kwargs):
        # verify the new in_out is in the right order and raise exception
        # if not.
        print "IN SAVE"
        try:
            # get the previous stamp
            # TODO: clean out in_out checking
            last = Timestamp.objects.filter(
                user=self.user,
                stamp__lt=Timestamp.objects.get(pk=self.pk).stamp)
            last = last.latest('stamp')

            l_stamp = last.stamp
            print "{} -- {}".format(last.in_out, l_stamp)
            # if last.in_out == self.in_out:
            #     print 'RAISING ERROR'
            #     raise TimestampEntryError('IN/OUT not in correct order.')

            # Check of timestamp straddles more than one date
            if last.in_out == 'IN' and last.stamp.date() != self.stamp.date():
                # create an out stamp for previous day, and an instamp at
                # start of current day
                l_year, l_month, l_day = l_stamp.year, l_stamp.month, l_stamp.day
                out_stamp = datetime.datetime(
                    l_year, l_month, l_day, 23, 59, 59, tzinfo=T_ZONE
                )
                # create out stamp on previous day
                Timestamp.objects.create(
                    user=self.user,
                    stamp=out_stamp,
                    in_out='OUT'
                )
                s_stamp = self.stamp
                s_year, s_month, s_day = s_stamp.year, s_stamp.month, s_stamp.day
                in_stamp = datetime.datetime(
                    s_year, s_month, s_day, 0, 0, 1, tzinfo=T_ZONE
                )
                # create in stamp on current day
                Timestamp.objects.create(
                    user=self.user,
                    stamp=in_stamp,
                    in_out='IN'
                )
        except Timestamp.DoesNotExist:
            pass

        # save the requested timestamp.
        super(Timestamp, self).save(*args, **kwargs)


class TimestampEdits(models.Model):
    """
    Logs changes made to Timestamp instances made.
    """
    timestamp = models.ForeignKey(Timestamp, verbose_name="Changed StampID")
    changed_by = models.ForeignKey(
        User,
        verbose_name="Changed By",
        related_name="user_changed_by"
    )
    for_employee = models.ForeignKey(
        User,
        verbose_name="Original Employee",
        related_name="user_for_employee"
    )
    original_datetime = models.DateTimeField("Original Datetime")
    original_inout = models.CharField("In_Out", max_length=3)
    new_datetime = models.DateTimeField("New Datetime")
    new_inout = models.CharField("New In_Out", max_length=3)
    change_reason = models.CharField("Reason", max_length=255)
    date_changed = models.DateTimeField("Date Changed")

    class meta:
        verbose_name_plural = "TimestampEdits"


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