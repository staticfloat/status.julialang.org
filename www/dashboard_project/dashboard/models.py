from django.db import models
import django.utils.timezone
import ast

# A really neat helper class from stackoverflow:
# Transparently serializes lists of simple python types
# http://stackoverflow.com/questions/5216162/how-to-create-list-field-in-django
class ListField(models.TextField):
    __metaclass__ = models.SubfieldBase
    description = "Stores a python list"

    def __init__(self, *args, **kwargs):
        super(ListField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if not value:
            value = []

        if isinstance(value, list):
            return value

        return ast.literal_eval(value)

    def get_prep_value(self, value):
        if value is None:
            return value

        return unicode(value)

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_db_prep_value(value)



# Stores the last successful build of a nightly
class NightlyBuild(models.Model):
    # The last successful build
    build_time = models.DateTimeField('Last Successful build')

    # The target this build is for ("OSX Nightly", "Ubuntu Nightly", etc...)
    target = models.TextField('Target Executable')

    # download URL
    url = models.TextField('Download URL')

    def __unicode__(self):
        return "Last build for %s"%(self.target if len(self.target) else "(no target)")


# These are the branches we want to track on the status page
class TravisBranch(models.Model):
    branch = models.TextField('Branch')

    def __unicode__(self):
        return self.branch


# Stores Travis build results
class TravisBuild(models.Model):
    # Time of this build
    build_time = models.DateTimeField('Time of the build')

    # Branch of this build
    branch = models.ForeignKey(TravisBranch)

    # commit hash of this build
    commit = models.TextField('Commit')

    # Result
    result = models.TextField('Result')

    def __unicode__(self):
        return self.commit + " [" + self.result + "]"
