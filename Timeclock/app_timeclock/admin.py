from django.contrib import admin
from app_timeclock.models import Timestamp


class TimestampAdmin(admin.ModelAdmin):
    list_display = ('stamp', 'user', 'in_out')
    list_filter = ['user']
    ordering = ['stamp']


admin.site.register(Timestamp, TimestampAdmin)