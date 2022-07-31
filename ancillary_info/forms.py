from django.forms import ModelForm
from calculated_stats.models import DcfVariables


class DCFForm(ModelForm):
    class Meta:
        model = DcfVariables
        fields = ['value']
