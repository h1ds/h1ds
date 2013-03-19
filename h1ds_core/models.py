"""Model classes for h1ds_core

H1DS Core contains models for communicating between H1DS modules.


"""
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models


if hasattr(settings, "WORKSHEETS_PUBLIC_BY_DEFAULT"):
    public_worksheets_default = settings.WORKSHEETS_PUBLIC_BY_DEFAULT
else:
    public_worksheets_default = False



class H1DSSignal(models.Model):
    """Identifier for signals passed though the H1DS system."""
    name = models.CharField(max_length=50, unique=True, help_text="Name of signal")
    description = models.CharField(max_length=500, help_text="Description of signal")

    def natural_key(self):
        return (self.name,)

    def __unicode__(self):
        return unicode(self.name)

class H1DSSignalInstance(models.Model):
    """Records an instance of an H1DS signal."""
    signal = models.ForeignKey(H1DSSignal)
    time = models.DateTimeField(auto_now_add=True)
    value = models.CharField(max_length=1024, blank=True)

    def __unicode__(self):
        return unicode("%s: %s" %(self.time, self.signal))
    
    class Meta:
        ordering = ('-time',)
        get_latest_by = 'time'


class Pagelet(models.Model):
    name = models.CharField(max_length=1024)
    pagelet_type = models.CharField(max_length=128)
    url = models.URLField(max_length=2048)
        
class Worksheet(models.Model):
    """A page for users to organise and store content."""
    user = models.ForeignKey(User)
    name = models.CharField(max_length=256)
    description = models.TextField()
    is_public = models.BooleanField(default=public_worksheets_default)
    pagelets = models.ManyToManyField(Pagelet, through='PageletCoordinates')

class PageletCoordinates(models.Model):
    pagelet = models.ForeignKey(Pagelet)
    worksheet = models.ForeignKey(Worksheet)
    coordinates = models.CharField(max_length=128)

    def get_coordinates(self):
        pass
    
