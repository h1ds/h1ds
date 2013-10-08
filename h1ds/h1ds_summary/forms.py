from django.forms import ModelForm
from h1ds_summary.models import SummaryAttribute


class SummaryAttributeForm(ModelForm):
    class Meta:
        model = SummaryAttribute
        # The device is determined by the data URL, so don't give user the
        # option to modify it.
        exclude = ('device', )


