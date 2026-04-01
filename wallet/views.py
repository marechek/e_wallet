from django.shortcuts import render, redirect
from django.http import HttpResponseForbidden
from .forms import TransactionForm, UserForm, WalletForm
from .models import Transaction, Wallet, TransactionType

from django.contrib.auth.models import User
from django.db.models import Q, Sum

from django.contrib.auth.decorators import login_required
from .forms import RegisterForm
from django.contrib.auth import login


@login_required
def transaction_create(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.wallet = request.user.wallet
            transaction.save()
            return redirect('transaction_list')
    else:
        form = TransactionForm()

    return render(request, 'wallet/transaction_form.html', {'form': form})


@login_required
def transaction_list(request):

    # ===== WALLET =====
    wallet, _ = Wallet.objects.get_or_create(user=request.user)

    # ===== BASE QUERY (SIEMPRE FILTRADA POR USUARIO) =====
    transactions = Transaction.objects.select_related(
        'wallet',
        'transaction_type'
    ).filter(wallet=wallet).order_by('-timestamp')

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

    # ===== DASHBOARD (CONSISTENTE CON FILTROS) =====
    total_depositos = transactions.filter(
        transaction_type__name='deposito'
    ).aggregate(total=Sum('amount'))['total'] or 0

    total_retiros = transactions.filter(
        transaction_type__name='retiro'
    ).aggregate(total=Sum('amount'))['total'] or 0

    balance = total_depositos - total_retiros

    # ===== CONTEXTO =====
    return render(request, 'wallet/transaction_list.html', {
        'transactions': transactions,
        'wallet': wallet,
        'user': request.user,
        'transaction_types': TransactionType.objects.all(),
        'selected_type': transaction_type_id,
        'total_depositos': total_depositos,
        'total_retiros': total_retiros,
        'balance': balance,
    })

@login_required
def transaction_detail(request, pk):
    transaction = Transaction.objects.select_related('wallet', 'transaction_type').get(pk=pk, wallet__user=request.user)
    return render(request, 'wallet/transaction_detail.html', {'transaction': transaction})

@login_required
def transaction_update(request, pk):
    return HttpResponseForbidden("Las transacciones no pueden ser editadas.")

@login_required
def transaction_delete(request, pk):
    return HttpResponseForbidden("No permitido")

@login_required
def transaction_reverse(request, pk):
    original = Transaction.objects.get(pk=pk, wallet__user=request.user)

    reverse_type = TransactionType.objects.get(
        name='retiro' if original.transaction_type.name == 'deposito' else 'deposito'
    )

    Transaction.objects.create(
        wallet=original.wallet,
        transaction_type=reverse_type,
        amount=original.amount,
        description=f"Reversa de transacción #{original.id}"
    )

    return redirect('transaction_list')

@login_required
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

@login_required
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

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()

            login(request, user)
            return redirect('transaction_list')
    else:
        form = RegisterForm()

    return render(request, 'wallet/register.html', {'form': form})

