#!/usr/bin/env python
from datetime import timedelta, datetime
import json
import requests
import random
import string

# This is a test script to auto-generate a bunch of data for status.julialang.org (running locally, of course)



# Generate four nightly builds, each one 17 hours earlier than the next, starting from now:
targets = ["OSX 10.6", "OSX 10.7+", "Ubuntu", "Windows"]
for idx in range(len(targets)):
	date = datetime.now() - timedelta(hours=idx*17)
	obj = {	'target':targets[idx],
			'build_time':date.isoformat(),
			'url':'http://julialang.org/'+targets[idx]}

	headers = {'content-type':'application/json'}
	requests.post("http://localhost:8000/put/nightly", data=json.dumps(obj), headers=headers)


# Generates a random TravisBuild for the given branch, and up to [time_limit] days in the past
def generate_travis(branch, time_limit, time_min=1):
	date = datetime.now() - timedelta(seconds=random.randint(60*60*24*time_min,60*60*24*time_limit))
	commit = ''.join(random.choice('1234567890abcdef') for x in range(40))
	obj = {	'branch':branch,
			'committed_at':date.isoformat(),
			'commit':commit,
			'status_message':'Passed' if random.random() > .5 else 'Failed'}

	headers = {'content-type':'application/json'}
	requests.post("http://localhost:8000/put/travis", data=json.dumps(obj), headers=headers)

# Generate a bunch of random builds over the last 8 days for `master`
for idx in range(40):
	generate_travis('master', 8)


# Generate a bunch of random builds within the last 3 days, and within the last 40 days for `sf/debugtools`
for idx in range(20):
	generate_travis('sf/debugtools', 3)
	generate_travis('sf/debugtools', 40)

generate_travis('release-0.1', 100)
generate_travis('release-0.1', 300, 200)
