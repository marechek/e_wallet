from django.contrib import admin
from django.db.models import Sum, Case, When, DecimalField
from django.db.models.functions import Coalesce
from decimal import Decimal

from .models import Wallet, TransactionType, Transaction


from django.contrib import admin
from django.db.models import Sum, Case, When, DecimalField
from django.db.models.functions import Coalesce
from decimal import Decimal

from .models import Wallet, TransactionType, Transaction


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance_display', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'created_at', 'updated_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        return qs.annotate(
            total_deposit=Coalesce(Sum(
                Case(
                    When(transactions__transaction_type__code='deposit', then='transactions__amount'),
                    default=0,
                    output_field=DecimalField()
                )
            ), Decimal('0.00')),

            total_withdraw=Coalesce(Sum(
                Case(
                    When(transactions__transaction_type__code='withdraw', then='transactions__amount'),
                    default=0,
                    output_field=DecimalField()
                )
            ), Decimal('0.00')),
        )

    def balance_display(self, obj):
        return obj.total_deposit - obj.total_withdraw

    balance_display.short_description = 'Saldo'


@admin.register(TransactionType)
class TransactionTypeAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'description')
    list_filter = ('code',)
    search_fields = ('name', 'description')


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'transaction_type', 'amount', 'timestamp', 'description')
    list_filter = ('transaction_type', 'timestamp')
    search_fields = ('wallet__user__username', 'wallet__user__email', 'description')
    readonly_fields = ('timestamp',)

    def user(self, obj):
        return obj.wallet.user
    user.short_description = 'Usuario'

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
