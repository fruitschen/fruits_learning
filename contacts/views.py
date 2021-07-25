from django.conf import settings
from django.contrib import messages
from fruits_learning.decorators import staff_member_required
from django.urls import reverse
from django.shortcuts import render
from django.shortcuts import redirect
from django.views import View
from django.utils.decorators import method_decorator

from contacts.models import Contact
from contacts.forms import EmailForm


import logging
log = logging.getLogger('contacts.views')


class SendEmailView(View):
    @method_decorator(staff_member_required)
    def get(self, request):
        form = EmailForm(initial={'sender': settings.SERVER_EMAIL})
        context = {
            'hide_header_footer': True,
            'form': form,
        }
        return render(request, 'contacts/send_email.html', context)

    @method_decorator(staff_member_required)
    def post(self, request):
        form = EmailForm(request.POST)
        if form.is_valid():
            email = form.save()
            email.send()
            send_email_url = reverse('contacts_send_email')
            messages.add_message(request, messages.SUCCESS, 'Email was sent. ')
            return redirect(send_email_url)
        else:
            context = {
                'hide_header_footer': True,
                'form': form,
            }
            return render(request, 'contacts/send_email.html', context)
