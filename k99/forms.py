from django.contrib.auth.forms import AuthenticationForm
from django.forms import ValidationError

class CustomAuthenticationForm(AuthenticationForm):
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if username is not None and password:
            user = authenticate(username=username, password=password)
            if user is None:
                try:
                    user = Customer.objects.get(username=username)
                    user.failed_login_attempts += 1
                    user.save()
                    if user.failed_login_attempts >= 5:
                        raise ValidationError("Your account is locked. Please contact support.")
                except Customer.DoesNotExist:
                    pass
        return super().clean()





