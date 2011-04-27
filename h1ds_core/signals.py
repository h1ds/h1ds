import django.dispatch

from h1ds_core.models import H1DSSignalInstance

h1ds_signal = django.dispatch.Signal(providing_args=["h1ds_sig"])

def create_instance(sender, **kwargs):
    new_instance = H1DSSignalInstance(signal=kwargs['h1ds_sig'])
    new_instance.save()

h1ds_signal.connect(create_instance)
