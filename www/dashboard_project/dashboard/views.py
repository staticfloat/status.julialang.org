from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
import json
from django.shortcuts import render
from models import *

def JSONResponse(data):
	return HttpResponse( json.dumps(data, cls=DjangoJSONEncoder), content_type="application/json" )

# Create your views here.
def index(request):
	#nightly_builds = NightlyBuild.objects.all()
	#travis_builds = TravisBuild.objects.all()
	#return render( request, 'dashboard/index.html', {'nightly_builds': nightly_builds, 'travis_builds': travis_builds})
	return render( request, 'dashboard/index.html')


# Returns a dict, indexed by target, pointing to the build_time
def get_nightly_builds(request):
	nightly_builds = NightlyBuild.objects.all()
	return JSONResponse({b.target:{'build_time':b.build_time, 'url':b.url} for b in nightly_builds})

# Returns a dict, indexed by branch
def get_travis_builds(request):
	travis_branches = TravisBranch.objects.all()

	all_builds = {}
	for branch in travis_branches:
		branch_builds = []
		for build in branch.travisbuild_set.all():
			branch_builds.append({'commit': build.commit, 'build_time': build.build_time, 'result': build.result })
		all_builds[branch.branch] = branch_builds;
	
	return JSONResponse(all_builds)

def get_package_builds(request):
	return JSONResponse({})