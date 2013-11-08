from django.conf.urls import patterns, include, url
from dashboard import views

urlpatterns = patterns('',
    url(r'^$', views.index),
    url(r'^get/travis', views.get_travis_builds),
    url(r'^put/travis', views.put_travis_build),
    url(r'^get/nightly', views.get_nightly_builds),
    url(r'^put/nightly', views.put_nightly_build),
    url(r'^put/clear_travis', views.clear_travis),
)
