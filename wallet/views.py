from django.shortcuts import render, redirect
from .forms import TransactionForm


def transaction_create(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('transaction_list')  # lo crearemos después
    else:
        form = TransactionForm()

    return render(request, 'wallet/transaction_form.html', {'form': form})