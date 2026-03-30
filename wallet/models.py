from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
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
        # Validación: no permitir montos negativos o cero
        if self.amount <= 0:
            raise ValidationError("El monto debe ser mayor a cero.")

        # Validación: evitar saldo negativo en retiros
        if self.transaction_type.name.lower() == 'retiro':
            if self.wallet.balance < self.amount:
                raise ValidationError("Saldo insuficiente para realizar el retiro.")

    def save(self, *args, **kwargs):
        # Ejecuta validaciones
        self.clean()

        # Actualiza balance según tipo de transacción
        if self.transaction_type.name.lower() == 'deposito':
            self.wallet.balance += self.amount

        elif self.transaction_type.name.lower() == 'retiro':
            self.wallet.balance -= self.amount

        # Guarda wallet actualizado
        self.wallet.save()

        # Guarda transacción
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.transaction_type.name} - {self.amount}"