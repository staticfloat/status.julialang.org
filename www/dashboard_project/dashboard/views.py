from django.http import HttpResponse, HttpResponseServerError, HttpResponseRedirect
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import render
from django.utils.timezone import now
from models import *
import urllib2, json

def JSONResponse(data):
	return HttpResponse( json.dumps(data, cls=DjangoJSONEncoder), content_type="application/json" )

# Updates a django model with a dict, mapping keys to properties inside that model.  Saves the model
def update_model( model, data, keys ):
	# If keys is a list, use same keys for model and data
	if type(keys) is list:
		for k in keys:
			if k in data:
				setattr(model, k, data[k])

	# If keys is a dict, use keys of keys for data, and values of keys for model:
	if type(keys) is dict:
		for k in keys:
			if k in data:
				setattr(model, keys[k], data[k])
	model.save()

# Create a dict from a model, ready for jsonification
def dict_model( model, keys ):
	d = {}
	for k in keys:
		d[k] = getattr(model,k)
	return d




# Returns a dict, indexed by target, pointing to the time
def get_nightly_builds(request):
	nightly_builds = NightlyBuild.objects.all()
	return JSONResponse({b.target:{'time':b.time, 'url':b.url, 'version':b.version} for b in nightly_builds})

# Store a nightly build
def put_nightly_build(request):
	if request.method == "POST":
		data = json.loads(request.body)

		# Find the old NightlyBuild, creating if it does not already exist.  Then update it.
		nightly_obj = NightlyBuild.objects.get_or_create(target=data['target'])[0]
		if not 'time' in data:
			nightly_obj.time = now()
		update_model( nightly_obj, data, ['time', 'url', 'version'] )

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

		# I like OK better than Passed
		if data['status_message'] == 'Passed':
			data['status_message'] = 'OK'

		# Find our branch
		branch = TravisBranch.objects.get_or_create(branch=data['branch'],defaults={'enabled':False})[0]

		# If we already have the commit that was sent in, delete that record
		travis_obj = TravisBuild.objects.get_or_create(commit=data['commit'], branch=branch)[0]
		update_model( travis_obj, data, {'committed_at':'time', 'status_message':'result'})
	return HttpResponse()


def get_codespeed_builds(request):
	json_obj = {}
	for env in CodespeedEnvironment.objects.all():
		codespeed_builds = CodespeedBuild.objects.filter(env=env)
		json_obj[env.name] = {b.blas:{'time': b.time, 'commit': b.commit} for b in codespeed_builds}
	return JSONResponse(json_obj)

def put_codespeed_build(request):
	if request.method == "POST":
		data = json.loads(request.body)

		# Do we already have this environment?  If not, drop the request
		env = CodespeedEnvironment.objects.filter(name=data['env'])
		if not len(env):
			return HttpResponse()

		# Delete the CodespeedBuild object that corresponds to this env/blas combo (if it exists)
		codespeed_obj = CodespeedBuild.objects.get_or_create(env=env[0],blas=data['blas'])[0]
		if not 'time' in data:
			codespeed_obj.time = now()
		update_model( codespeed_obj, data, ['commit', 'time'] )
	return HttpResponse()


def put_codespeed_environment(request):
	if request.method == "POST":
		data = json.loads(request.body)

		# Get the previous codespeed environment object, if it exists. Create one otherwise
		codespeedenv_obj = CodespeedEnvironment.objects.get_or_create(name=data['name'])[0]
		update_model( codespeedenv_obj, data, ['OS'])
	return HttpResponse()

def get_codespeed_environments(request):
	return JSONResponse({env.name:env.OS for env in CodespeedEnvironment.objects.all()})

def get_package_builds(request):
	# Get our JuliaVersionStatus object
	if not len(JuliaVersionStatus.objects.all()):
		return HttpResponseServerError('No JuliaVersionStatus objects created!')
	jvs = JuliaVersionStatus.objects.get()

	# Get all Package Builds for the currently configured stable and nightly builds
	data = PackageBuild.objects.filter(jlver=jvs.stable) | PackageBuild.objects.filter(jlver=jvs.nightly)

	# These are the fields we'll send from each PackageBuild
	fields = ['name', 'url', 'license', 'licfile', 'status', 'details', 'gitsha', 'pkgreq', 'travis', 'version', 'jlver', 'jlcommit', 'gitdate']

	# Create a dict out of each model, and point to it by each model's name
	obj = [dict_model(p, fields) for p in data]
	return JSONResponse(obj)

def put_package_build(request):
	if request.method == "POST":
		data = json.loads(request.body)

		# Update our "latest PackageEval" field
		if not len(PackageRun.objects.all()):
			PackageRun.objects.create()
		else:
			PackageRun.objects.update(date=now())

		# Delete this PackageBuild if it already exists
		package_obj = PackageBuild.objects.get_or_create(name=data['name'],jlver=data['jlver'])[0]
		update_model( package_obj, data, ['name', 'url', 'license', 'status', 'version', 'jlcommit', 'details', 'gitsha', 'gitdate', 'licfile'] )

		# Special treatment for boolean values
		for key in ['pkgreq', 'travis']:
			if key in data:
				setattr(package_obj, key, data[key] == "true")
		package_obj.save()
	return HttpResponse()


def get_package_log(request, jlverstr, pkgname):
	# Get our JuliaVersionStatus object
	if not len(JuliaVersionStatus.objects.all()):
		return HttpResponseServerError('No JuliaVersionStatus objects created!')
	jvs = JuliaVersionStatus.objects.get()

	# Get all Package Builds for the currently configured stable and nightly builds
	data = []
	if jlverstr.lower() == 'stable':
		data = PackageBuild.objects.filter(jlver=jvs.stable, name=pkgname)
	elif jlverstr.lower() == 'nightly':
		data = PackageBuild.objects.filter(jlver=jvs.nightly, name=pkgname)
	else:
		return HttpResponseServerError('Invalid julia version type ' + jlverstr)

	if len(data) == 0:
		return HttpResponseServerError('No ' +jlverstr.lower()+ ' packages found that match ' + pkgname)

	return HttpResponse(data.get().testlog)


def get_package_run(request):
	if len(PackageRun.objects.all()):
		return JSONResponse({'date':PackageRun.objects.get().date})
	return HttpResponseServerError('No PackageRun objects created!')

def get_julia_version_status(request):
	if len(JuliaVersionStatus.objects.all()):
		jvs = JuliaVersionStatus.objects.get()
		return JSONResponse({'stable':jvs.stable, 'nightly':jvs.nightly})
	return HttpResponseServerError('No JuliaVersionStatus objects created!')

def clear_travis(request):
	TravisBuild.objects.all().delete()
	TravisBranch.objects.all().delete()
	return HttpResponse("\_[;_;]_/<br/>sad robot is sad, yet filled with joy")

def get_latest(request, target):
	nightly_builds = NightlyBuild.objects.filter(target=target)
	if not len(nightly_builds):
		return HttpResponse("No such build target \"%s\""%(target))
	return HttpResponseRedirect(nightly_builds[0].url)

def get_stable(request, target):
	stable_builds = StableBuild.objects.filter(target=target)
	if not len(stable_builds):
		return HttpResponse("No such build target \"%s\""%(target))
	return HttpResponseRedirect(stable_builds[0].url)
