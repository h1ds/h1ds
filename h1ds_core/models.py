"""Model classes for h1ds_core

H1DS Core contains models for communicating between H1DS modules.


"""

from django.db import models


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

    def __unicode__(self):
        return unicode("%s: %s" %(self.time, self.signal))
    
    class Meta:
        ordering = ('-time',)
        get_latest_by = 'time'

