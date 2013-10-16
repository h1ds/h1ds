"""Add specified shots."""
from optparse import make_option
from django.core.management.base import BaseCommand
from h1ds.models import Shot, Device


class Command(BaseCommand):
    args = '<shot_number shot_number ...>'
    help = 'Add specified shots.'
    option_list = BaseCommand.option_list + (
        make_option('-d', '--device',
                    dest='device',
                    help='Device to add shot to (use slug string)'
                    ),
    )

    def handle(self, *args, **options):
        if options['device']:
            device = Device.objects.get(slug=options['device'])
        else:
            device = Device.objects.get(is_default=True)
        for shot_number in map(int, args):
            s = Shot(number=shot_number, device=device)
            s.save()
            self.stdout.write('Successfully added shot %d' % shot_number)
