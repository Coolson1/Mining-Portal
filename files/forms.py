from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import StudentProfile


class StudentRegistrationForm(UserCreationForm):
    # Extend UserCreationForm to collect email, first/last/middle names and level.
    # Make all name/email fields required per user's request.
    first_name = forms.CharField(max_length=150, required=True)
    middle_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    level = forms.ChoiceField(choices=StudentProfile._meta.get_field('level').choices, required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'middle_name', 'last_name', 'email', 'level', 'password1', 'password2')

    def save(self, commit=True):
        # Save the User instance first, then create the StudentProfile with middle_name and level.
        user = super().save(commit=False)
        # Ensure the password is set correctly on the user object even when
        # `commit=False` was used by the parent form implementation.
        password = self.cleaned_data.get('password1')
        if password:
            user.set_password(password)
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        user.email = self.cleaned_data.get('email', '')
        if commit:
            user.save()
            # Create or update StudentProfile
            StudentProfile.objects.update_or_create(
                user=user,
                defaults={
                    'middle_name': self.cleaned_data.get('middle_name', ''),
                    'level': int(self.cleaned_data.get('level')),
                }
            )
        return user

    def clean(self):
        # Ensure all required fields are present and non-empty; raise a single
        # ValidationError if any required field is missing so the user sees one
        # clear message about completing every field.
        cleaned = super().clean()
        required_fields = ['username', 'first_name', 'middle_name', 'last_name', 'email', 'level', 'password1', 'password2']
        missing = []
        for f in required_fields:
            val = cleaned.get(f)
            if val is None or (isinstance(val, str) and not val.strip()):
                missing.append(f)
        if missing:
            # Show a short, simple message when any required field is missing.
            raise ValidationError('please fill all fields')
        return cleaned

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username and User.objects.filter(username__iexact=username).exists():
            raise ValidationError('A user with that username already exists.')
        return username
