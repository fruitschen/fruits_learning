# -*- coding: UTF-8 -*-
from django import forms

from contacts.models import Email
from dal import autocomplete


class EmailForm(autocomplete.FutureModelForm):

    class Meta:
        model = Email
        exclude = ['is_mailed', 'mailed_at', ]
        widgets = {
            'recipients': autocomplete.ModelSelect2Multiple(
                'contacts-autocomplete'
            )
        }
