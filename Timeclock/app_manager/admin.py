from django.contrib import admin
from app_manager.models import Employee


class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('user', 'current_wage')
    list_filter = ['user']

admin.site.register(Employee, EmployeeAdmin)