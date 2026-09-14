from django import forms

from django.contrib.auth import authenticate


class LoginForm(forms.Form):

    email = forms.EmailField(
        label='Email Address',
        widget = forms.EmailInput(attrs={'placeholder':'Enter your email address', 'autocomplete':'email',}),)


    password = forms.CharField(label='Password',
                               widget = forms.PasswordInput(attrs={'placeholder':'Enter your password', 'autocomplete':'email',
                                                                   }
                                                                   ),)

    def clean(self):

        cleaned_data = super().clean()

        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if not email or not password:
            return cleaned_data

        user = authenticate(username=email, password=password,)

        if user is None:
            raise forms.ValidationError('Invalid email address or password.')

        if not user.is_active:
            raise forms.ValidationError('Your account is inactive.')

        self.user = user
        return cleaned_data