"""Add specified shots."""
from optparse import make_option
import itertools
from django.core.management.base import BaseCommand
from h1ds.models import Shot, Device


def parse_shot_args(args):
    individual_shots = []
    shot_ranges = []
    for arg in args:
        if "-" in arg:
            shot_ranges.append(map(int, arg.split('-')))
        else:
            individual_shots.append(int(arg))
    collected_shots = [range(i[0], i[1]+1) for i in shot_ranges]
    collected_shots.append(individual_shots)
    return sorted(set(itertools.chain(*collected_shots)), reverse=True)


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
        for shot_number in parse_shot_args(args):
            shot, created = Shot.objects.get_or_create(number=shot_number, device=device)
            if created:
                self.stdout.write('Successfully added shot %d' % shot_number)
            else:
                self.stdout.write('Shot %d exists, ignoring.' % shot_number)
