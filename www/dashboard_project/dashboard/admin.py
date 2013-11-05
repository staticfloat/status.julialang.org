from django.contrib import admin
from dashboard.models import *

admin.site.register(NightlyBuild)
admin.site.register(TravisBranch)
admin.site.register(TravisBuild)