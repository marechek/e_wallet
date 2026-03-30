from django.shortcuts import render, redirect
from .forms import TransactionForm
from .models import Transaction


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
    transactions = Transaction.objects.select_related('wallet', 'transaction_type').all().order_by('-timestamp')
    return render(request, 'wallet/transaction_list.html', {'transactions': transactions})