import re
import pandas as pd
from typing import Tuple

class BankFileParser:
    @staticmethod
    def parse_file(filepath: str) -> Tuple[pd.DataFrame, str, str]:
        filename = filepath.split('/')[-1].lower()
        if 'chase' in filename:
            return BankFileParser._parse_chase(filepath)
        elif 'crypto' in filename:
            return BankFileParser._parse_crypto_com(filepath)
        elif 'bank of america' in filename or 'bankamerica' in filename:
            return BankFileParser._parse_bank_of_america(filepath)
        elif 'capital one' in filename:
            return BankFileParser._parse_capital_one(filepath)
        else:
            raise ValueError(f"Unknown bank file format: {filename}")

    @staticmethod
    def _parse_chase(filepath: str) -> Tuple[pd.DataFrame, str, str]:
        df = pd.read_csv(filepath)
        bank_name = 'Chase'
        card_number = BankFileParser._extract_card_from_filename(filepath)
        return df, bank_name, card_number

    @staticmethod
    def _parse_crypto_com(filepath: str) -> Tuple[pd.DataFrame, str, str]:
        df = pd.read_csv(filepath)
        bank_name = 'Crypto.com'
        card_number = BankFileParser._extract_card_from_filename(filepath)
        return df, bank_name, card_number

    @staticmethod
    def _parse_bank_of_america(filepath: str) -> Tuple[pd.DataFrame, str, str]:
        df = pd.read_csv(filepath)
        bank_name = 'Bank of America'
        card_number = BankFileParser._extract_card_from_filename(filepath)
        return df, bank_name, card_number

    @staticmethod
    def _parse_capital_one(filepath: str) -> Tuple[pd.DataFrame, str, str]:
        df = pd.read_csv(filepath)
        bank_name = 'Capital One'
        card_number = BankFileParser._extract_capital_one_card(df)
        return df, bank_name, card_number

    @staticmethod
    def _extract_card_from_filename(filename: str) -> str:
        match = re.search(r'(\d{4})(?=\s*\.csv)', filename)
        if match:
            return match.group(1)
        match = re.search(r'\D(\d{4})\D', filename)
        if match:
            return match.group(1)
        return '0000'  # Default if no card number found

    @staticmethod
    def _extract_capital_one_card(df: pd.DataFrame) -> str:
        card_column = next((col for col in df.columns if 'card' in col.lower() and 'no' in col.lower()), None)
        if card_column and not df[card_column].isna().all():
            return df[card_column].iloc[0][-4:]  # Last 4 digits of the first non-null value
        return '0000'  # Default if no card number found

    @staticmethod
    def get_date_column(df: pd.DataFrame) -> str:
        possible_date_columns = ['Timestamp', 'Timestamp (UTC)', 'Transaction Date', 'DATE', 'Date']
        for column in possible_date_columns:
            if column in df.columns:
                return column
        raise ValueError("No valid date column found in the data.")

    @staticmethod
    def get_amount_column(df: pd.DataFrame) -> str:
        amount_columns = [col for col in df.columns if 'amount' in col.lower() or 'debit' in col.lower() or 'credit' in col.lower()]
        if amount_columns:
            return amount_columns[0]
        raise ValueError("No valid amount column found in the data.")

    @staticmethod
    def get_description_column(df: pd.DataFrame) -> str:
        description_columns = ['Description', 'TRANSACTION DETAILS', 'Merchant', 'Payee', 'Transaction Description', 'Memo', 'Name', 'Transaction']
        for col in description_columns:
            if col in df.columns:
                return col
        raise ValueError("No valid description column found in the data.")