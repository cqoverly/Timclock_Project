"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import datetime
from datetime import timedelta

from django.test import TestCase
from django.contrib.auth.models import User
import django.utils as utils

import pytz

from models import *

# class BlogAdminTestCase(TestCase):
#     def setUp(self):
#         self.client = Client()
#
#         s = self.client.session
#         s['the_answer_to_life_and_everything'] = 42
#         s.save()
#
#     # Actual Tests Here...
#
#
# class SimpleTest(TestCase):
#     def test_basic_addition(self):
#         """
#         Tests that 1 + 1 always equals 2.
#         """
#         self.assertEqual(1 + 1, 2)


#### MODELS #####

class TimestampModelTestCase(TestCase):

    def setUp(self):
        self.test_user = User.objects.create_user(
            'testuser3',
            'testuser@testemail.com',
            'password'
        )

        self.pacific = pytz.timezone('US/Pacific')
        self.date = datetime.datetime(2013, 11, 8, 8, 00, tzinfo=self.pacific)
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


class TimestampEditsTestCase(TestCase):

    def setUp(self):
        self.pacific = pytz.timezone('US/Pacific')
        self.date = datetime.datetime(2013, 11, 8, 8, 00, tzinfo=self.pacific)
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
            new.original_datetime.astimezone(self.pacific),
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




