from django.db import models
from django.core.mail import send_mail
from django.utils import timezone


class Contact(models.Model):
    first_name = models.CharField("First name", max_length=100)
    last_name = models.CharField("Last name", max_length=50)
    email = models.EmailField("E-mail address", max_length=75, unique=True)

    @property
    def full_name(self):
        return '{} {}'.format(self.first_name, self.last_name)

    def __unicode__(self):
        return self.full_name


class Email(models.Model):
    subject = models.CharField(max_length=256)
    sender = models.CharField(max_length=256)
    recipients = models.ManyToManyField(Contact, related_name='sent_emails')
    content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_mailed = models.BooleanField(default=False)
    mailed_at = models.DateTimeField(null=True, blank=True)

    @property
    def recipients_emails_list(self):
        emails = self.recipients.all().values_list('email', flat=True)
        return emails

    def __unicode__(self):
        return '{} to {} sent at {}'.format(self.subject, self.recipients_emails_list, self.mailed_at)

    def send(self):
        send_mail(
            self.subject,
            self.content,
            self.sender,
            self.recipients_emails_list,
            fail_silently=False)
        self.is_mailed = True
        self.mailed_at = timezone.now()
        self.save()
