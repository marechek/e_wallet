from functools import wraps
from django.shortcuts import render
from .forms import TransactionForm


def wallet_required_active(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        wallet = request.user.wallet

        if not wallet.is_active:
            return render(request, 'wallet/transaction_form.html', {
                'form': TransactionForm(),
                'wallet_inactive': True
            })

        return view_func(request, *args, **kwargs)

    return _wrapped_view