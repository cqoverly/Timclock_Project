# Python standard library imports
import datetime
from datetime import timedelta

# Django framework imports
from django.test import TestCase
from django.contrib.auth.models import User
import django.utils as utils

# 3rd party imports
import pytz

# Project imports
from models import *

T_ZONE = pytz.timezone(settings.TIME_ZONE)


class TimestampModelTestCase(TestCase):

    def setUp(self):
        self.test_user = User.objects.create_user(
            'testuser3',
            'testuser@testemail.com',
            'password'
        )

        self.date = datetime.datetime(2013, 10, 15, 8, 00, tzinfo=T_ZONE)
        self.test_entry = Timestamp(
            user=self.test_user,
            stamp=self.date,
            in_out='IN'
        )
        self.test_entry.save()
        self.retrieved_stamp = Timestamp.objects.filter(user=self.test_user).latest('stamp')

    def test_create_timestamp(self):
        user = User.objects.get(username='testuser3')
        # self.assertEqual(self.test_entry, self.retrieved_stamp)
        self.assertEqual(self.retrieved_stamp, self.test_entry)

    def test_check_inout(self):
        self.assertEqual(self.retrieved_stamp.in_out, 'IN')

    def test_check_stamp(self):
        self.assertEqual(self.retrieved_stamp.stamp, self.date)

    def test_check_employee(self):
        self.assertEqual(self.retrieved_stamp.user, self.test_user)

    def test_set_inout(self):
        next_inout = Timestamp.set_inout(self.test_user)
        self.assertEqual(next_inout, 'OUT')

    def test_incorrect_inout(self):
        stamp = datetime.datetime(2013, 10, 15, 16, 00, tzinfo=T_ZONE)
        params = {'user': self.test_user, 'stamp': stamp, 'in_out': 'IN'}
        self.assertRaises(
            TimestampEntryError,
            Timestamp.objects.create,
            **params
        )

    def test_overnight_stamp(self):
        """
        Test to ensure that a work period that clocks in on one day but
        clock out the next creates 3 stamps, an out on the start day, a new
        in on the requested out day, and the originally requested out.
        """
        stamp = datetime.datetime(2013, 10, 16, 1, 23, 32, tzinfo=T_ZONE)
        in_out = 'OUT'
        user = self.test_user
        new_ts = Timestamp.objects.create(user=user, stamp=stamp, in_out=in_out)
        day1_outstamp = datetime.datetime(2013, 10, 15, 23, 59, 59, tzinfo=T_ZONE)
        day2_instamp = datetime.datetime(2013, 10, 16, 0, 0, 1, tzinfo=T_ZONE)
        d1_outts = Timestamp.objects.get(stamp=day1_outstamp)
        d2_intts = Timestamp.objects.get(stamp=day2_instamp)
        orig_ts = Timestamp.objects.filter(user=self.test_user).latest('stamp')
        self.assertEqual(new_ts, orig_ts)
        self.assertEqual(d1_outts.in_out, 'OUT')
        self.assertEqual(d2_intts.in_out, 'IN')


class TimestampEditsTestCase(TestCase):

    def setUp(self):
        self.date = datetime.datetime(2013, 11, 15, 8, 00, tzinfo=T_ZONE)
        self.request_user = User.objects.create_user(
            'testuser2',
            'testuser2@testmail.com',
            'password'
        )
        self.test_employee = User.objects.create_user(
            'testuser3',
            'testuser@testemail.com',
            'password'
        )
        self.delta = timedelta(minutes=5)
        self.orig_stamp = Timestamp(
            user=self.test_employee,
            stamp=self.date,
            in_out='IN'
        )
        self.orig_stamp.save()
        self.minutes = self.orig_stamp.stamp.minute
        self.new_datetime = self.orig_stamp.stamp + self.delta
        self.reason = "Test reason."
        self.record = TimestampEdits.objects.create(
            timestamp=self.orig_stamp,
            changed_by=self.request_user,
            for_employee=self.orig_stamp.user,
            original_datetime=self.orig_stamp.stamp,
            original_inout=self.orig_stamp.in_out,
            new_datetime=self.new_datetime,
            new_inout=self.orig_stamp.in_out,
            change_reason=self.reason,
            date_changed=utils.timezone.now()
        )
        self.record.save()
        employee = self.orig_stamp.user
        self.edit_entry = TimestampEdits.objects.filter(for_employee=employee)
        self.edit_entry = self.edit_entry.latest('date_changed')

    def test_create(self):

        self.assertIsInstance(self.edit_entry, TimestampEdits)

    def test_attributes(self):
        new, old = self.edit_entry, self.orig_stamp
        self.assertEquals(new.timestamp, old)
        self.assertEquals(new.changed_by, self.request_user)
        self.assertEquals(new.for_employee, old.user)
        self.assertEquals(
            new.original_datetime.astimezone(T_ZONE),
            old.stamp
        )
        self.assertEqual(
            new.original_inout,
            old.in_out
        )
        self.assertEqual(new.new_datetime, old.stamp + self.delta)
        self.assertEqual(new.new_inout, old.in_out)
        self.assertEqual(new.change_reason, self.reason)
        self.assertIsInstance(new.date_changed, datetime.datetime)




