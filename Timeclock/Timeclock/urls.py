from django.conf.urls import patterns, include, url
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from app_manager.views import vw_login

urlpatterns = patterns('',
    # Examples:
    url(r'^login/$',
        vw_login,
        name='login'),
    url(r'^logout/$',
        'django.contrib.auth.views.logout',
        {'next_page': '/'},
        name='logout'),
    url(r'^$', include('app_manager.urls')),
    url(r'^manage/', include('app_manager.urls')),
    url(r'^timeclock/', include('app_timeclock.urls')),
    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
)
