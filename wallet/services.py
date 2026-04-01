from django.core.exceptions import ValidationError


class WalletInactiveError(ValidationError):
    pass


def validate_wallet_active(wallet):
    if not wallet.is_active:
        raise WalletInactiveError("La billetera está desactivada.")