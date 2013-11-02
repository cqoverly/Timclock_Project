from django.db import models
from django.contrib.auth.models import User
# import django.utils
# import datetime
# from datetime import timedelta
# import calendar
# import pytz

# from django.core.exceptions import DoesNotExist

# Create your models here.

# from DjangoTest.settings import TIME_ZONE


#MOVED TO .methods_classes.py

# TZ = pytz.timezone(TIME_ZONE)
# UTC = pytz.timezone('utc')
# WEEKDAYS = ['Sun', 'Mon', 'Tues', 'Wed', 'Thur', 'Fri', 'Sat']
# WEEKDAY_NUMBERS = [6, 0, 1, 2, 3, 4, 5, 6]
# WEEKDAY_DICT = dict(zip(WEEKDAYS, WEEKDAY_NUMBERS))


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
            # Most likely because new employee cloking in for first time.
            return 'IN'
        if last_stamp.in_out == 'IN':
            return 'OUT'
        elif last_stamp.in_out == 'OUT':
            return 'IN'
        # If all else fails
        else:
            raise AttributeError

    def edit_timestamp(self):
        """
        Updates a change in a Timestamp instance.
        """
        pass


class TimestampEdits(models.Model):
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



