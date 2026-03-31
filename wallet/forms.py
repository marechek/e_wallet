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
    username = forms.CharField(disabled=True, label="Usuario")
    first_name = forms.CharField(disabled=True, label="Nombre")
    last_name = forms.CharField(disabled=True, label="Apellido")

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

class WalletForm(forms.ModelForm):
    class Meta:
        model = Wallet
        fields = ['is_active']

class RegisterForm(UserCreationForm):
    first_name = forms.CharField(label="Nombre")
    last_name = forms.CharField(label="Apellido")
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']

