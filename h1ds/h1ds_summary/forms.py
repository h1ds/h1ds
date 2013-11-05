from django import forms
from h1ds.models import Device
from h1ds_summary.models import SummaryAttribute
from h1ds_summary.validators import shotslug_validator, attributeslug_validator
from h1ds_summary.parsers import parse_shot_slug, parse_attr_str
class SummaryAttributeForm(forms.ModelForm):
    class Meta:
        model = SummaryAttribute
        # The device is determined by the data URL, so don't give user the
        # option to modify it.
        exclude = ('device', )


class ControlPanelForm(forms.Form):
    DEVICE_CHOICES = tuple((d.slug, d.name) for d in Device.objects.all())
    device = forms.ChoiceField(widget=forms.Select, choices=DEVICE_CHOICES)
    shots = forms.CharField(max_length=256,
                            validators=[shotslug_validator],
                            help_text='list (url syntax) of shots to recompute, or "all"')
    attributes = forms.CharField(max_length=264,
                                 validators=[attributeslug_validator],
                                 help_text='list (url syntax) of attributes to recompute, or "all"')

    def get_cleaned_data_for_device(self, device):
        cleaned_data = self.clean()
        cleaned_data['shots'] = parse_shot_slug(device, cleaned_data['shots'])
        cleaned_data['attributes'] = parse_attr_str(device, cleaned_data['attributes'])
        return cleaned_data

class RawSqlForm(forms.Form):
    DEVICE_CHOICES = tuple((d.slug, d.name) for d in Device.objects.all())
    device = forms.ChoiceField(widget=forms.Select, choices=DEVICE_CHOICES)
    select = forms.CharField(widget=forms.Textarea)
    where = forms.CharField(widget=forms.Textarea)
