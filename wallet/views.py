from django.shortcuts import render, redirect
from .forms import TransactionForm
from .models import Transaction
from django.http import HttpResponseForbidden
from django.contrib.auth.models import User
from .models import Wallet


def transaction_create(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('transaction_list')  # lo crearemos después
    else:
        form = TransactionForm()

    return render(request, 'wallet/transaction_form.html', {'form': form})

def transaction_list(request):
    transactions = Transaction.objects.select_related(
        'wallet',
        'wallet__user',
        'transaction_type'
    ).all().order_by('-timestamp')

    wallet = Wallet.objects.first()
    user = wallet.user if wallet else None

    return render(request, 'wallet/transaction_list.html', {
        'transactions': transactions,
        'wallet': wallet,
        'user': user
    })

def transaction_detail(request, pk):
    transaction = Transaction.objects.select_related('wallet', 'transaction_type').get(pk=pk)
    return render(request, 'wallet/transaction_detail.html', {'transaction': transaction})

def transaction_update(request, pk):
    return HttpResponseForbidden("Las transacciones no pueden ser editadas.")

def transaction_delete(request, pk):
    transaction = Transaction.objects.get(pk=pk)

    if request.method == 'POST':
        transaction.delete()
        return redirect('transaction_list')

    return render(request, 'wallet/transaction_confirm_delete.html', {'transaction': transaction})

def user_update(request, pk):
    user = User.objects.get(pk=pk)

    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('transaction_list')
    else:
        form = UserForm(instance=user)

    return render(request, 'wallet/user_form.html', {'form': form})

def wallet_update(request, pk):
    wallet = Wallet.objects.get(pk=pk)

    if request.method == 'POST':
        form = WalletForm(request.POST, instance=wallet)
        if form.is_valid():
            form.save()
            return redirect('transaction_list')
    else:
        form = WalletForm(instance=wallet)

    return render(request, 'wallet/wallet_form.html', {'form': form})

