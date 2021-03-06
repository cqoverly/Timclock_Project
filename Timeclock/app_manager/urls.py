from django.conf.urls import patterns,  url

import views

urlpatterns = patterns('',
    # Examples:
    url(r'^$', views.vw_home, name='home'),
    url(r'^edit_employee/(?P<pk>\d+)/$', views.vw_edit_employee, name='edit_emp'),
    url(r'^add_employee$', views.vw_add_employee, name='add_emp'),
    url(r'^change_password$', views.vw_change_password, name='change_password'),
    url(r'^view_employees$', views.EmployeeList.as_view(), name='view_emps'),
    url(r'^view_employee/(?P<pk>\d+)$',
        views.vw_employee_detail,
        name='view_emp'),
    )