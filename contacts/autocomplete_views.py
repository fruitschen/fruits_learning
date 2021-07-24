from dal import autocomplete
from django.db.models import Q

from .models import Contact


class ContactAutocomplete(autocomplete.Select2QuerySetView):
    
    def get_queryset(self):
        
        if not self.request.user.is_authenticated and self.request.user.is_staff:
            return Contact.objects.none()

        qs = Contact.objects.all()
        val = self.q.strip()
        
        if self.q:
            if ' ' in val:
                val, val2 = val.split()
                qs = qs.filter(
                    Q(first_name__istartswith=val) &
                    Q(last_name__istartswith=val2)
                )
            else:
                qs = qs.filter(
                    Q(email__istartswith=val) |
                    Q(first_name__istartswith=val) |
                    Q(last_name__istartswith=val)
                )
                
        return qs
