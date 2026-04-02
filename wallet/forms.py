from django import forms
from django.contrib.auth.models import User
from .models import Wallet, Transaction, TransactionType
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.db.models import Sum
from django.db.models.functions import Coalesce

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['transaction_type', 'amount', 'description']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            self.fields['amount'].disabled = True
            self.fields['transaction_type'].disabled = True

    def clean(self):
        cleaned_data = super().clean()

        transaction_type = cleaned_data.get('transaction_type')
        amount = cleaned_data.get('amount')

        if not transaction_type or not amount or not self.user:
            return cleaned_data

        if transaction_type.name.lower() == 'retiro':
            wallet = self.user.wallet

            from decimal import Decimal
            from django.db.models import Sum
            from django.db.models.functions import Coalesce

            total_depositos = Transaction.objects.filter(
                wallet=wallet,
                transaction_type__name='deposito'
            ).aggregate(
                total=Coalesce(Sum('amount'), Decimal('0.00'))
            )['total']

            total_retiros = Transaction.objects.filter(
                wallet=wallet,
                transaction_type__name='retiro'
            ).aggregate(
                total=Coalesce(Sum('amount'), Decimal('0.00'))
            )['total']

            balance = total_depositos - total_retiros

            if amount > balance:
                self.add_error(None, "Saldo insuficiente para realizar el retiro.")

        return cleaned_data

class TransactionTypeForm(forms.ModelForm):
    class Meta:
        model = TransactionType
        fields = ['name', 'description']

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs.update({
            'autofocus': 'autofocus'
        })