from django.conf.urls import patterns, url

import views


urlpatterns = patterns('',
    # Examples:
    url(r'^punch_clock$', views.vw_punch_clock, name='punch_clock'),
    url(r'^view_timecard$', views.vw_view_timecard, name='view_card'),
    url(r'^edit_timestamp/(?P<pk>\d+)$', views.vw_edit_timestamp, name='edit_stamp'),
)