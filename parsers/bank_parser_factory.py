from .capital_one_parser import CapitalOneParser
from .crypto_com_parser import CryptoComParser
from .chase_parser import ChaseParser
from .bank_of_america_parser import BankOfAmericaParser

def get_parser(bank_name: str):
    if bank_name == 'capital_one':
        return CapitalOneParser()
    elif bank_name == 'crypto_com':
        return CryptoComParser()
    elif bank_name == 'chase':
        return ChaseParser()
    elif bank_name == 'bank_of_america':
        return BankOfAmericaParser()
    else:
        return None