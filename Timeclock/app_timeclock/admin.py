from django.contrib import admin
from app_timeclock.models import Timestamp, TimestampEdits


class TimestampAdmin(admin.ModelAdmin):
    list_display = ('stamp', 'user', 'in_out')
    list_filter = ['user']
    ordering = ['stamp']


class TimestampEditsAdmin(admin.ModelAdmin):
    list_display = (
        'changed_by',
        'for_employee',
        'original_datetime',
        'original_inout',
        'new_datetime',
        'new_inout',
        'change_reason',
        'date_changed',
    )

    list_filter = ['for_employee']
    ordering = ['new_datetime']


admin.site.register(Timestamp, TimestampAdmin)
admin.site.register(TimestampEdits, TimestampEditsAdmin)
