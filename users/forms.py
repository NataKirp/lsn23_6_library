from django.contrib.auth.forms import UserCreationForm
from django import forms

from users.models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    phone_number = forms.CharField(label='Номер телефона', max_length=15, required=False,
                                   help_text='Необязательное поле. Введите ваш номер телефона.')
    username = forms.CharField(label='Имя пользователя (логин)', max_length=50, required=True)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('email', 'username', 'first_name', 'last_name', 'phone_number')
        # fields = ('email', 'username', 'first_name', 'last_name', 'phone_number', 'password1', 'password2')
        labels = {'email': 'Электронная почта',}

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number and not phone_number.isdigit():
            raise forms.ValidationError('Номер телефона должен состоять только из цифр')
        return phone_number
