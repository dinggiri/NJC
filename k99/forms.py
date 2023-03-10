from django.contrib.auth.forms import AuthenticationForm
from django.forms import ValidationError
from django.contrib.auth import authenticate
from k99.models import Customer

class CustomAuthenticationForm(AuthenticationForm):
    def clean(self):
        admin_list = ['admin', '24566905', '40106905', '40426905', 'test']
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if username is not None and password:
            user = authenticate(username=username, password=password)
            if user is None:
                try:
                    user = Customer.objects.get(username=username)
                    if username not in admin_list:
                        user.failed_login_attempts += 1
                    user.save()
                    if user.failed_login_attempts >= 5:
                        raise ValidationError("비밀번호 입력 오류 5회 이상으로, 더 이상 사용하실 수 없습니다. 010-4010-6905으로 연락바랍니다.")
                except Customer.DoesNotExist:
                    pass
            else:
                if user.failed_login_attempts >= 5:
                    raise ValidationError("비밀번호 입력 오류 5회 이상으로, 더 이상 사용하실 수 없습니다. 010-4010-6905으로 연락바랍니다.")
        return super().clean()





