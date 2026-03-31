from django import forms
from .models import Transaction
from django.contrib.auth.models import User
from .models import Wallet
from django.contrib.auth.forms import UserCreationForm


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['transaction_type', 'amount', 'description']

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']

class WalletForm(forms.ModelForm):
    class Meta:
        model = Wallet
        fields = ['is_active']

class RegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

