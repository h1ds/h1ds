"""Add specified shots."""
from django.core.management.base import BaseCommand, CommandError
from h1ds.models import Shot

class Command(BaseCommand):
    args = '<shot_number shot_number ...>'
    help = 'Add specified shots.'

    def handle(self, *args, **kwargs):
        for shot_number in map(int, args):
            s = Shot(number=shot_number)
            s.save()
            self.stdout.write('Successfully added shot %d' % shot_number)
