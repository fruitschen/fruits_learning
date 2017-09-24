from django.conf.urls import *
from contacts.views import *
from contacts.autocomplete_views import ContactAutocomplete

urlpatterns = [
    url(r'^send_email/$', SendEmailView.as_view(), name='contacts_send_email'),
    url(r'^autocomplete/$', ContactAutocomplete.as_view(), name='contacts-autocomplete', ),
]
