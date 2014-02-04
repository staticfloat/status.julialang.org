from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import render
from django.utils.timezone import now
import json
from models import *
import urllib2

def JSONResponse(data):
	return HttpResponse( json.dumps(data, cls=DjangoJSONEncoder), content_type="application/json" )

# We've only got one template, and it's barely a template at all!
def index(request):
	return render( request, 'dashboard/index.html')

# Returns a dict, indexed by target, pointing to the time
def get_nightly_builds(request):
	nightly_builds = NightlyBuild.objects.all()
	return JSONResponse({b.target:{'time':b.time, 'url':b.url} for b in nightly_builds})

# Store a nightly build
def put_nightly_build(request):
	if request.method == "POST":
		data = json.loads(request.body)

		# Delete the old NightlyBuild:
		NightlyBuild.objects.filter(target=data['target']).delete()

		# If 'time' was ommitted, just use the current time
		time = now()
		if 'time' in data:
			time = data['time']

		NightlyBuild.objects.create(target=data['target'],url=data['url'],time=time)
	return HttpResponse()

# Returns a dict, indexed by branch
def get_travis_builds(request):
	travis_branches = TravisBranch.objects.filter(enabled=True)

	all_builds = {}
	for branch in travis_branches:
		branch_builds = []
		for build in branch.travisbuild_set.all():
			branch_builds.append({'commit': build.commit, 'time': build.time, 'result': build.result })
		all_builds[branch.branch] = branch_builds;
	
	return JSONResponse(all_builds)

def put_travis_build(request):
	if request.method == "POST":
		data = None

		# Travis gives us form-encoded JSON.  Hooray.
		if request.body[:8] == "payload=":
			data = json.loads(urllib2.unquote(request.body[8:]))
		else:
			data = json.loads(request.body)

		# If we already have the commit that was sent in, delete that record
		TravisBuild.objects.filter(commit=data['commit']).delete()

		# Find our branch
		branch = TravisBranch.objects.get_or_create(branch=data['branch'],defaults={'enabled':False})[0]

		# I like OK better than Passed
		if data['status_message'] == 'Passed':
			data['status_message'] = 'OK'

		# Create our TravisBuild object with the requisite data
		TravisBuild.objects.create(	commit = data['commit'],
									time = data['committed_at'],
									branch = branch,
									result = data['status_message'])
	return HttpResponse()

def put_codespeed_build(request):
	if request.method == "POST":
		data = json.loads(request.body)

		# Do we already have this environment?  If not, drop the request
		try:
			env = CodespeedEnvironment.objects.get(name=data['env'])

			# Delete the CodespeedBuild object that corresponds to this env/blas combo (if it exists)
			CodespeedBuild.objects.filter(env=env,blas=data['blas']).delete()

			# If 'time' was ommitted, just use the current time
			time = now()
			if 'time' in data:
				time = data['time']

			# Create a new one and store it
			CodespeedBuild.objects.create(env=env,blas=data['blas'], time=time, commit=data['commit'])
		except:
			pass
	return HttpResponse()


def get_codespeed_builds(request):
	json_obj = {}
	for env in CodespeedEnvironment.objects.all():
		codespeed_builds = CodespeedBuild.objects.filter(env=env)
		json_obj[env.name] = {b.blas:{'time': b.time, 'commit': b.commit} for b in codespeed_builds}
	return JSONResponse(json_obj)

def put_codespeed_environment(request):
	if request.method == "POST":
		data = json.loads(request.body)

		# Delete this environment object if it already exists
		CodespeedEnvironment.objects.filter(name=data['name']).delete()

		# Create a new one and store it
		CodespeedEnvironment.objects.create(name=data['name'],OS=data['OS'])
	return HttpResponse()

def get_codespeed_environments(request):
	return JSONResponse({env.name:env.OS for env in CodespeedEnvironment.objects.all()})

def get_package_builds(request):
	data = PackageBuild.objects.all()
	obj = {p.name:{	'url':p.url, 'license':p.license, 'status':p.status, 'details':p.details, 'gitsha':p.gitsha,
					'pkgreq':p.pkgreq, 'metareq':p.metareq, 'travis':p.travis, 'version':p.version} for p in data}
	return JSONResponse(obj)

def put_package_build(request):
	if request.method == "POST":
		data = json.loads(request.body)

		# Update our "latest PackageEval" field
		if not len(PackageRun.objects.all()):
			PackageRun.objects.create(date=now())
		else:
			pr_obj = PackageRun.objects.get()
			pr_obj.date = now()
			pr_obj.save()

		# Delete this PackageBuild if it already exists
		PackageBuild.objects.filter(name=data['name']).delete()

		# Save out the information to our database
		PackageBuild.objects.create(name=data['name'], url=data['url'], license=data['license'], status=data['status'],
									version=data['version'], details=data['details'], gitsha=data['gitsha'],
									pkgreq=data['pkgreq'] == "true", metareq=data['metareq'] == "true", travis=data['travis'] == "true")
	return HttpResponse()


def get_package_run(request):
	pr_obj = PackageRun.objects.get()
	return JSONResponse({'date':pr_obj.date})

def clear_travis(request):
	TravisBuild.objects.all().delete()
	TravisBranch.objects.all().delete()
	return HttpResponse("\_[;_;]_/<br/>sad robot is sad, yet filled with joy")
