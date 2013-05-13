import django.dispatch

from h1ds_core.models import H1DSSignal, H1DSSignalInstance

h1ds_signal = django.dispatch.Signal(providing_args=["h1ds_sig", "value"])

def create_instance(sender, **kwargs):
    new_instance = H1DSSignalInstance(signal=kwargs['h1ds_sig'],
                                      value=kwargs.get('value', ""))
    new_instance.save()

h1ds_signal.connect(create_instance)

new_shot_inst, c = H1DSSignal.objects.get_or_create(name="new_shot",
                                                    description="New Shot")

class NewShotEvent(object):
    def __init__(self, shot_number):
        self.shot_number = shot_number
    def send_event(self):
        h1ds_signal.send(sender=self,
                         h1ds_sig=new_shot_inst,
                         value=self.shot_number)
