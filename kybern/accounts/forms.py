from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from django_registration.forms import RegistrationForm

from accounts.models import User


def validate_access_code(value):
    """The access code field is validated against a list of codes that can be given to users who want to sign up."""
    valid_codes = ['alpha-adjs', 'alpha-eias', 'alpha-fhhe', 'alpha-imet', 'alpha-ergt', 'alpha-styl', 'alpha-hiir'] 
    if value.lower() not in valid_codes:
        raise ValidationError(
            _('%(value)s is not a valid access code.'),
            params={'value': value},
        )


class RegistrationFormWithCode(RegistrationForm):
    """Overrides django_registration's Registration Form to add the AccessCodeField with custom validation."""

    access_code = forms.CharField(label='Your access code', max_length=100, validators=[validate_access_code])

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email exists")
        return email
