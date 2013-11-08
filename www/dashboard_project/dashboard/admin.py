from django.contrib import admin
from dashboard.models import *

class TravisBuildAdmin(admin.ModelAdmin):
	list_display = ('commit', 'branch', 'result', 'build_time')

admin.site.register(NightlyBuild)
admin.site.register(TravisBranch)
admin.site.register(TravisBuild, TravisBuildAdmin)