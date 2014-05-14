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


# Stores information about the last PackageRun (there can be only one!)
class PackageRun(models.Model):
    date = models.DateTimeField('Date of last PackageEval.jl submission', default=now)


# Stores the current stable and nightly versions (in MAJOR.MINOR) format
class JuliaVersionStatus(models.Model):
    # Stable version (0.2)
    stable = models.TextField('Stable Version Number')

    # Nightly version (0.3)
    nightly = models.TextField('Nightly Verison Number')


# Stores Package builds from PackageEval
class PackageBuild(models.Model):
    # The name of the package (Nettle.jl)
    name = models.TextField('Name')

    # The url of the package (http://github.com/JuliaLang/Nettle.jl)
    url = models.TextField('Repository URL')

    # The version of Julia this package was tested against (0.2/deadbeef)
    jlver = models.TextField('Julia version')
    jlcommit = models.TextField('Julia commit')

    # The version of the package being tested (v0.1.8)
    version = models.TextField('Version of package (from METADATA)')

    # The SHA and date of the git commit being tested (baadf00d/2014-01-29 11:43:44 -0500)
    gitsha = models.TextField('git SHA of package')
    gitdate = models.TextField('Date of commit of current version')

    # License of the package (MIT/LICENSE.md)
    license = models.TextField('License type')
    licfile = models.TextField('License file path')

    # Details ("Tests Exist, tried 'using pkgname' but failed", etc...)
    details = models.TextField('Details')

    # status, must be one of ["full_pass", "full_fail", "using_pass", "using_fail"]
    status = models.TextField('Status')

    # Flags for specific checks from Package Eval (true/false)
    pkgreq = models.BooleanField('Package REQUIRE file present', default=False)
    travis = models.BooleanField('Travis setup', default=False)

    # Full log output of a testing run
    testlog = models.TextField('Test log')

    def __unicode__(self):
        return self.name
