from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from django_registration.forms import RegistrationForm

from accounts.models import User


class RegistrationFormCleanEmail(RegistrationForm):
    """Overrides django_registration's Registration Form to add the AccessCodeField with custom validation."""

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email exists")
        return email
