from django.conf.urls import patterns, include, url
from dashboard import views

urlpatterns = patterns('',
    url(r'^get/travis$', views.get_travis_builds),
    url(r'^put/travis$', views.put_travis_build),
    url(r'^put/clear_travis$', views.clear_travis),
    url(r'^get/nightly$', views.get_nightly_builds),
    url(r'^put/nightly$', views.put_nightly_build),
    url(r'^get/codespeed$', views.get_codespeed_builds),
    url(r'^put/codespeed$', views.put_codespeed_build),
    url(r'^get/codespeed_envs$', views.get_codespeed_environments),
    url(r'^put/codespeed_env$', views.put_codespeed_environment),

    url(r'^download/(.+)', views.get_latest),
    url(r'^stable/(.+)', views.get_stable),
)
