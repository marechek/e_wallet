from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from decimal import Decimal
from django.db.models import Sum
from django.db.models.functions import Coalesce


class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Wallet de {self.user.username} - Saldo: {self.balance}"


class TransactionType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Transaction(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.ForeignKey(TransactionType, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.amount <= 0:
            raise ValidationError("El monto debe ser mayor a cero.")

        if not self.wallet_id:
            return

        if self.transaction_type.name.lower() == 'retiro':
            from .models import Transaction

            total_depositos = Transaction.objects.filter(
                wallet=self.wallet,
                transaction_type__name='deposito'
            ).aggregate(
                total=Coalesce(Sum('amount'), Decimal('0.00'))
            )['total']

            total_retiros = Transaction.objects.filter(
                wallet=self.wallet,
                transaction_type__name='retiro'
            ).aggregate(
                total=Coalesce(Sum('amount'), Decimal('0.00'))
            )['total']

            balance_actual = total_depositos - total_retiros

            if self.amount > balance_actual:
                raise ValidationError("Saldo insuficiente para realizar el retiro.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.transaction_type.name} - {self.amount}"

