from django.shortcuts import render, redirect
from django.http import HttpResponseForbidden
from .forms import TransactionForm, UserForm, WalletForm
from .models import Transaction, Wallet, TransactionType

from django.contrib.auth.models import User
from django.db.models import Q
from django.db.models import Sum


def transaction_create(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('transaction_list')  # lo crearemos después
    else:
        form = TransactionForm()

    return render(request, 'wallet/transaction_form.html', {'form': form})

from django.db.models import Q, Sum
from .models import Transaction, Wallet, TransactionType


def transaction_list(request):
    transactions = Transaction.objects.select_related(
        'wallet',
        'wallet__user',
        'transaction_type'
    ).all().order_by('-timestamp')

    # ===== FILTROS =====
    transaction_type_id = request.GET.get('type')
    min_amount = request.GET.get('min_amount')
    search = request.GET.get('search')

    if transaction_type_id:
        transactions = transactions.filter(transaction_type_id=transaction_type_id)

    if min_amount:
        transactions = transactions.filter(amount__gte=min_amount)

    if search:
        transactions = transactions.filter(
            Q(description__icontains=search) |
            Q(transaction_type__name__icontains=search)
        )

    # ===== DASHBOARD (AQUÍ VA LO NUEVO) =====
    total_depositos = Transaction.objects.filter(
        transaction_type__name='deposito'
    ).aggregate(total=Sum('amount'))['total'] or 0

    total_retiros = Transaction.objects.filter(
        transaction_type__name='retiro'
    ).aggregate(total=Sum('amount'))['total'] or 0

    wallet = Wallet.objects.first()
    user = wallet.user if wallet else None
    transaction_types = TransactionType.objects.all()

    # ===== CONTEXTO =====
    return render(request, 'wallet/transaction_list.html', {
        'transactions': transactions,
        'wallet': wallet,
        'user': user,
        'transaction_types': transaction_types,
        'selected_type': transaction_type_id,
        'total_depositos': total_depositos,
        'total_retiros': total_retiros,
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

