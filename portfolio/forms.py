from django import forms
from .models import Transactions


class TransactionsForm(forms.ModelForm):

    # create meta class
    class Meta:
        # specify model to be used
        model = Transactions

        # specify fields to be used
        fields = [
            "company",
            "decision",
            "date_dealt",
            "date_settled",
            "reference",
            "num_stock",
            "price",
            "fees",
        ]
