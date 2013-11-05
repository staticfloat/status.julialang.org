from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()
import dashboard.urls

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'dashboard_project.views.home', name='home'),
    # url(r'^dashboard_project/', include('dashboard_project.foo.urls')),

    url(r'', include(dashboard.urls)),
    url(r'^admin/', include(admin.site.urls)),
)
