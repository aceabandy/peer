from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth.forms import PasswordResetForm
from django.core.exceptions import ValidationError
# Define your custom login form
class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)

    username = forms.CharField(widget=forms.TextInput(attrs={
        "class": "input",
        "type": "text",
        "placeholder": "Enter username",
    }))
    
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        "class": "input",
        "type": "password",
        "placeholder": "Enter password",
    }))
class UserRegistrationForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        "class": "input",
        "type": "text",
        "placeholder": "Enter username",
    }), label="Username")
    
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        "class": "input",
        "type": "email",
        "placeholder": "Enter your email",
    }), label="Email")

    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        "class": "input",
        "placeholder": "Enter your password",
        "id": "password1",
    }), label="Password")

    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        "class": "input",
        "placeholder": "Repeat password",
        "id": "password2",
    }), label="Confirm Password")

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email is already registered.")
        return email





class DepositForm(forms.Form):
    username = forms.CharField(max_length=100)
    cryptocurrency = forms.ChoiceField(choices=[
        ('btc', 'BTC'),
        ('eth', 'ETH'),
        ('ltc', 'LTC'),
        ('doge', 'DOGE'),
        ('sol', 'SOL'),
        ('bnb', 'BNB'),
        ('ton', 'TONCOIN'),
        ('bch', 'BCH'),
        ('tron', 'TRON'),
        

    ])         



class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email address'})
    )

    # You can add additional customizations if needed
    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Add custom email validation logic here if needed
        return email
    



class SendMoneyForm(forms.Form):
    recipient = forms.CharField(
        label="Recipient Username",
        max_length=150,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter recipient's username"}),
    )
    amount = forms.DecimalField(
        label="Amount",
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "Enter amount to send", "min": 1}),
    )

    def clean_recipient(self):
        recipient_username = self.cleaned_data.get("recipient")
        try:
            recipient = User.objects.get(username=recipient_username)
            return recipient
        except User.DoesNotExist:
            raise forms.ValidationError("The recipient username does not exist.")

    def clean_amount(self):
        amount = self.cleaned_data.get("amount")
        if amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero.")
        return amount    