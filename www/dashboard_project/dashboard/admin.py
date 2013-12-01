from django.contrib import admin
from dashboard.models import *

class TravisBuildAdmin(admin.ModelAdmin):
	list_display = ('commit', 'branch', 'result', 'time')

admin.site.register(NightlyBuild)
admin.site.register(TravisBranch)
admin.site.register(TravisBuild, TravisBuildAdmin)
admin.site.register(CodespeedBuild)
admin.site.register(CodespeedEnvironment)
admin.site.register(PackageBuild)