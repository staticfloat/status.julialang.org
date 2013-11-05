from django.conf.urls import patterns, include, url
from dashboard import views

urlpatterns = patterns('',
    url(r'^$', views.index),
    url(r'^get/travis', views.get_travis_builds),
    url(r'^get/nightly', views.get_nightly_builds),
)
