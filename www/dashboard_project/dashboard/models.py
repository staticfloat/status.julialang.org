from django.db import models
from django.utils.timezone import now
import ast

# Stores the last successful build of a nightly
class NightlyBuild(models.Model):
    # The last successful build
    time = models.DateTimeField('Last Successful build', default=now)

    # The target this build is for ("osx10.7+", "win64", etc...)
    target = models.TextField('Target Executable')

    # The version string of this build
    version = models.TextField('Version string')

    # download URL
    url = models.TextField('Download URL')

    def __unicode__(self):
        return "Last build for %s"%(self.target if len(self.target) else "(no target)")


class StableBuild(models.Model):
    # The target this build is for ("osx10.7+", "win64", etc...)
    target = models.TextField('Target Executable')

    # download URL
    url = models.TextField('Download URL')

    def __unicode__(self):
        return "Stable build link for %s"%(self.target if len(self.target) else "(no target)")


# Environment for a codespeed build ("criid", "julia", etc...)
class CodespeedEnvironment(models.Model):
    name = models.TextField('Environment name')
    OS = models.TextField('Operating System')

    def __unicode__(self):
        return self.name

# Stores the last successful codespeed build
class CodespeedBuild(models.Model):
    # Environment this build was built in
    env = models.ForeignKey(CodespeedEnvironment)

    # Backing BLAS implementation
    blas = models.TextField('Backing BLAS')

    # The last successful build
    time = models.DateTimeField('Last successful build', default=now)

    # The hash of the build
    commit = models.TextField('Commit Hash')

    def __unicode__(self):
        return self.env.name + " [" + self.blas + "]"

# These are the branches we want to track on the status page
class TravisBranch(models.Model):
    # The name of the branch ("master", "release-0.1", etc...)
    branch = models.TextField('Branch')

    # Whether this branch is enabled or not
    enabled = models.BooleanField('Enabled')

    def __unicode__(self):
        return self.branch


# Stores Travis build results
class TravisBuild(models.Model):
    # Time of this build
    time = models.DateTimeField('Time of the build', default=now)

    # Branch of this build
    branch = models.ForeignKey(TravisBranch)

    # commit hash of this build
    commit = models.TextField('Commit')

    # Result
    result = models.TextField('Result')

    def __unicode__(self):
        return self.commit + " [" + self.result + "]"
