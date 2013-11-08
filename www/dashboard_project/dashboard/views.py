from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import render
from django.utils.timezone import now
import json
from models import *

def JSONResponse(data):
	return HttpResponse( json.dumps(data, cls=DjangoJSONEncoder), content_type="application/json" )

# Create your views here.
def index(request):
	return render( request, 'dashboard/index.html')


# Returns a dict, indexed by target, pointing to the build_time
def get_nightly_builds(request):
	nightly_builds = NightlyBuild.objects.all()
	return JSONResponse({b.target:{'build_time':b.build_time, 'url':b.url} for b in nightly_builds})

def put_nightly_build(request):
	if request.method == "POST":
		data = json.loads(request.body)

		# Delete the old NightlyBuild:
		NightlyBuild.objects.filter(target=data['target']).delete()

		build_time = now()
		if 'build_time' in data:
			build_time = data['build_time']

		NightlyBuild.objects.create(target=data['target'],build_time=build_time)
	return HttpResponse()

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

def put_travis_build(request):
	if request.method == "POST":
		data = None
		if request.body[:8] == "payload=":
			data = json.loads(request.body[:8])
		else:
			data = json.loads(request.body)

		# If we already have the commit that was sent in, delete that record
		TravisBuild.objects.filter(commit=data['commit']).delete()

		# Find our branch
		branch = TravisBranch.objects.get_or_create(branch=data['branch'])[0]

		# I like OK better than Passed
		if data['status_message'] == 'Passed':
			data['status_message'] = 'OK'

		# Create our TravisBuild object with the requisite data
		TravisBuild.objects.create(	commit = data['commit'],
									build_time = data['committed_at'],
									branch = branch,
									result = data['status_message'])
	return HttpResponse()

def get_package_builds(request):
	return JSONResponse({})

def put_package_build(request):
	return HttpResponse()

def clear_travis(request):
	TravisBuild.objects.all().delete()
	TravisBranch.objects.all().delete()
	return HttpResponse("\_[;_;]_/<br/>sad robot is sad, yet filled with joy")