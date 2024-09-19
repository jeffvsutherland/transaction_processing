# bank_file_identifier.py

import re

class BankFileIdentifier:
    @staticmethod
    def identify_bank(filename):
        filename = filename.lower()
        if "chase" in filename:
            return "Chase"
        elif "crypto_com" in filename or "crypto.com" in filename:
            return "Crypto.com"
        elif "bank america" in filename or "bankamerica" in filename:
            return "Bank of America"
        elif "capitalone" in filename or "capital one" in filename:
            return "Capital One"
        else:
            raise ValueError(f"Unknown bank file format: {filename}")
