from django import forms

class RegisterForm(forms.Form):
    username = forms.CharField(max_length=150, label='Username')
    email = forms.EmailField(required=True, label='Email')
    password = forms.CharField(widget=forms.PasswordInput, label='Password')
    password_confirm = forms.CharField(widget=forms.PasswordInput, label='Confirm Password')

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            self.add_error("password_confirm", "Password don't match!")
        return cleaned_data

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, label='user name')
    password = forms.CharField(widget=forms.PasswordInput, label='password')