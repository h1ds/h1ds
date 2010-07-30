from django.db import models

DATATYPE_CHOICES = (
    ('F', 'Float'),
    ('I', 'Integer'),
    ('D', 'Date and time'),
    ('T', 'Text'),
    )

class SummaryAttribute(models.Model):
    slug = models.SlugField(max_length=100, help_text="Name of the attribute as it appears in the URL")
    name = models.CharField(max_length=500, help_text="Full name of the attribute")
    source = models.CharField(max_length=1000, help_text="Path to script on the filesystem which takes a shot number as a single argument and returns the attribute value")
    description = models.TextField()
    data_type = models.CharField(max_length=1, choices=DATATYPE_CHOICES, help_text="Data type used to store attribute in database")

class Shot(models.Model):
    shot = models.IntegerField(primary_key=True)

class FloatAttributeInstance(models.Model):
    shot = models.ForeignKey(Shot)
    attribute = models.ForeignKet(SummaryAttribute)
    value = models.FloatField()
