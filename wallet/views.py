from django.shortcuts import render, redirect
from django.http import HttpResponseForbidden
from .forms import TransactionForm, UserForm, WalletForm
from .models import Transaction, Wallet, TransactionType

from django.contrib.auth.models import User
from django.db.models import Q, Sum

from django.contrib.auth.decorators import login_required
from .forms import RegisterForm
from django.contrib.auth import login
from django.core.exceptions import ValidationError


from django.core.exceptions import ValidationError
from .services import validate_wallet_active, WalletInactiveError
from .decorators import wallet_required_active

@login_required
@wallet_required_active
def transaction_create(request):
    wallet, _ = Wallet.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = TransactionForm(request.POST)

        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.wallet = wallet

            try:
                from decimal import Decimal
                from django.db.models import Sum
                from django.db.models.functions import Coalesce

                total_depositos = Transaction.objects.filter(
                    wallet=wallet,
                    transaction_type__name='deposito'
                ).aggregate(total=Coalesce(Sum('amount'), Decimal('0.00')))['total']

                total_retiros = Transaction.objects.filter(
                    wallet=wallet,
                    transaction_type__name='retiro'
                ).aggregate(total=Coalesce(Sum('amount'), Decimal('0.00')))['total']

                balance = total_depositos - total_retiros

                if transaction.transaction_type.name.lower() == 'retiro' and transaction.amount > balance:
                    raise ValidationError("Saldo insuficiente para realizar el retiro.")

                transaction.save()
                return redirect('transaction_list')

            except ValidationError as e:
                for error in e.messages:
                    form.add_error(None, error)

    else:
        form = TransactionForm()

    return render(request, 'wallet/transaction_form.html', {'form': form})


@login_required
def transaction_list(request):

    # ===== WALLET =====
    wallet, _ = Wallet.objects.get_or_create(user=request.user)

    # ===== BASE QUERY (SIEMPRE FILTRADA POR USUARIO) =====
    base_qs = Transaction.objects.select_related(
        'wallet',
        'transaction_type'
    ).filter(wallet=wallet)

    transactions = base_qs.order_by('-timestamp')

    # ===== DASHBOARD (SIEMPRE SOBRE BASE) =====
    total_depositos = base_qs.filter(
        transaction_type__name='deposito'
    ).aggregate(total=Sum('amount'))['total'] or 0

    total_retiros = base_qs.filter(
        transaction_type__name='retiro'
    ).aggregate(total=Sum('amount'))['total'] or 0

    balance = total_depositos - total_retiros

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
@wallet_required_active
def transaction_reverse(request):
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

