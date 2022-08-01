from django.forms import ModelForm
from .models import DcfVariables


class DCFForm(ModelForm):
    class Meta:
        model = DcfVariables
        fields = [
            "est_growth_rate",
            "est_disc_rate",
            "est_ltg_rate",
            ]
