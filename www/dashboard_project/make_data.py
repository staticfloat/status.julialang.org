#!/usr/bin/env python
from datetime import timedelta, datetime
import json, os, requests, random, string, sys

# This is a test script to auto-generate a bunch of data for status.julialang.org (running locally, of course)
# It requires the [requests] module to run properly


# Generate four nightly builds, each one 17 hours earlier than the next, starting from now:
print 'Uploading nightly builds....'
targets = ["OSX 10.6", "OSX 10.7+", "Ubuntu", "Windows"]
for idx in range(len(targets)):
	date = datetime.now() - timedelta(hours=idx*17)
	obj = {	'target':targets[idx],
			'time':date.isoformat(),
			'url':'http://julialang.org/'+targets[idx]}

	requests.post("http://localhost:8000/put/nightly", data=json.dumps(obj))


print 'Uploading Codespeed environments/builds....'
def put_env(name, os):
	obj = {'name': name, 'OS':os}
	requests.post("http://localhost:8000/put/codespeed_env", data=json.dumps(obj))

# Generate the codespeed envs first
put_env('batman', 'Batnix 10.1')
put_env('superman', 'Cryptonix 8.0')

# Generate some random codepeed builds as well
for env in ["batman", "superman"]:
	for blas in ["openblas", "closeblas"]:
		date = datetime.now() - timedelta(hours=random.randint(1,72))
		obj = {	'env':env,
				'blas':blas,
				'commit': ''.join(random.choice('1234567890abcdef') for x in range(40)),
				'time':date.isoformat()}

		requests.post("http://localhost:8000/put/codespeed", data=json.dumps(obj))


print 'Uploading Travis builds.... (note you must explicitly enable branches)'
# Generates a random TravisBuild for the given branch, and up to [time_limit] days in the past
def generate_travis(branch, time_limit, time_min=1):
	date = datetime.now() - timedelta(seconds=random.randint(60*60*24*time_min,60*60*24*time_limit))
	commit = ''.join(random.choice('1234567890abcdef') for x in range(40))
	obj = {	'branch':branch,
			'committed_at':date.isoformat(),
			'commit':commit,
			'status_message':'Passed' if random.random() > .2 else 'Failed'}

	requests.post("http://localhost:8000/put/travis", data=json.dumps(obj))

# Generate a bunch of random builds over the last 8 days for `master`
for idx in range(40):
	generate_travis('master', 8)

# Generate a bunch of random builds within the last 3 days, and within the last 40 days for `sf/debugtools`
for idx in range(20):
	generate_travis('sf/debugtools', 3)
	generate_travis('sf/debugtools', 40)

generate_travis('release-0.1', 100)
generate_travis('release-0.1', 300, 200)


print 'Uploading package builds....'
for f in os.listdir('testdata'):
	if f.endswith('.json'):
		data = open("testdata/%s"%(f,)).read()
		requests.post("http://localhost:8000/put/package", data=data)
