from django.conf.urls import patterns, url

import views


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'DjangoTest.views.home', name='home'),
    # url(r'^DjangoTest/', include('DjangoTest.foo.urls')),
    url(r'^punch_clock$', views.vw_punch_clock, name='punch_clock'),
    url(r'^view_timecard$', views.vw_view_timecard, name='view_card'),
)