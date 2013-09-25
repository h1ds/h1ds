from django.forms import ModelForm
from h1ds_summary.models import SummaryAttribute


class SummaryAttributeForm(ModelForm):
    class Meta:
        model = SummaryAttribute


