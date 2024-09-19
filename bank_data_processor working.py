# bank_data_processor.py

import os
import pandas as pd
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BankDataProcessor:
    def __init__(self, input_dir: str, output_dir: str, rules_processor):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.rules_processor = rules_processor
        self.files_used = set()
        self.errors = []

    def process_bank_files(self, start_date: datetime, end_date: datetime):
        intermediate_files = {}
        input_files = {}
        bank_files = [f for f in os.listdir(self.input_dir) if f.lower().endswith('.csv')]

        logger.info(f"Found {len(bank_files)} CSV files in the input directory")
        for file in bank_files:
            logger.info(f"  - {file}")

        if not bank_files:
            logger.warning(f"No CSV files found in the input directory: {self.input_dir}")
            return intermediate_files, input_files

        for bank_file in bank_files:
            filepath = os.path.join(self.input_dir, bank_file)
            logger.info(f"Processing file: {bank_file}")
            try:
                df = self.process_bank_file(filepath, bank_file, start_date, end_date)
                if df is not None and not df.empty:
                    intermediate_files[bank_file] = df
                    input_files[bank_file] = list(df.columns)
                    self.files_used.add(os.path.relpath(filepath, self.input_dir))
                    logger.info(f"Successfully processed {bank_file}. Shape: {df.shape}")

                    intermediate_file_path = os.path.join(self.output_dir, f"intermediate_{bank_file}")
                    df.to_csv(intermediate_file_path, index=False)
                    logger.info(f"Saved intermediate file: {intermediate_file_path}")
                else:
                    logger.warning(f"No data found in date range for file: {bank_file}")
            except Exception as e:
                error_msg = f"Error processing {bank_file}: {str(e)}"
                logger.error(error_msg, exc_info=True)
                self.errors.append(error_msg)

        return intermediate_files, input_files

    def process_bank_file(self, filepath: str, bank_file: str, start_date: datetime, end_date: datetime):
        df = pd.read_csv(filepath)
        logger.info(f"Original columns in {bank_file}: {df.columns.tolist()}")

        df = self.standardize_columns(df, bank_file)

        date_column = self.find_date_column(df)
        df = self.process_date(df, date_column)

        df = df[(df['Normalized Date'].dt.date >= start_date.date()) & (df['Normalized Date'].dt.date <= end_date.date())]

        if df.empty:
            logger.warning(f"No transactions found in the date range for file: {filepath}")
            return pd.DataFrame()

        # Add bank column
        df['Bank'] = self.get_bank_name(bank_file)
        logger.info(f"Added 'Bank' column. Unique values: {df['Bank'].unique()}")

        # Add card column with last four digits
        df['Card'] = self.get_card_number(df, bank_file)
        logger.info(f"Added 'Card' column. Unique values: {df['Card'].unique()}")

        # Handle Capital One transactions
        if 'Capital One' in df['Bank'].values:
            if 'Debit' in df.columns and 'Credit' in df.columns:
                df['Amount'] = df['Credit'].fillna(0) - df['Debit'].fillna(0)
            elif 'Amount' in df.columns:
                df['Amount'] = -df['Amount']  # Negate all amounts for Capital One

        # Ensure all Kindle transactions are treated as expenses
        df.loc[df['Description'].str.contains('kindle', case=False), 'Amount'] = -df.loc[df['Description'].str.contains('kindle', case=False), 'Amount'].abs()

        logger.info(f"Final columns: {df.columns.tolist()}")
        logger.info(f"Final shape: {df.shape}")

        return self.apply_rules(df)

    def standardize_columns(self, df: pd.DataFrame, bank_file: str):
        if 'Description' not in df.columns:
            if 'Transaction Description' in df.columns:
                df['Description'] = df['Transaction Description']
            elif 'DESCRIPTION' in df.columns:
                df['Description'] = df['DESCRIPTION']
            else:
                logger.warning(f"No 'Description' column found in {bank_file}. Using first available text column.")
                text_columns = df.select_dtypes(include=['object']).columns
                if len(text_columns) > 0:
                    df['Description'] = df[text_columns[0]]
                else:
                    df['Description'] = 'Unknown'

        if 'Amount' not in df.columns:
            if 'AMOUNT' in df.columns:
                df['Amount'] = df['AMOUNT']
            elif 'Debit' in df.columns and 'Credit' in df.columns:
                df['Amount'] = df['Debit'].fillna(0) - df['Credit'].fillna(0)
            else:
                logger.warning(f"No 'Amount' column found in {bank_file}. Using first available numeric column.")
                numeric_columns = df.select_dtypes(include=['number']).columns
                if len(numeric_columns) > 0:
                    df['Amount'] = df[numeric_columns[0]]
                else:
                    df['Amount'] = 0

        return df

    def find_date_column(self, df):
        possible_date_columns = ['Timestamp (UTC)', 'Transaction Date', 'DATE', 'Posted Date', 'Post Date']
        for col in possible_date_columns:
            if col in df.columns:
                return col
        raise ValueError("No date column found")

    def process_date(self, df, date_column):
        df['Normalized Date'] = pd.to_datetime(df[date_column])
        df['Date'] = df['Normalized Date'].dt.date
        df['Time'] = df['Normalized Date'].dt.time
        return df

    def get_bank_name(self, bank_file: str) -> str:
        bank_file_lower = bank_file.lower()
        if 'chase' in bank_file_lower:
            return 'Chase'
        elif 'crypto' in bank_file_lower:
            return 'Crypto.com'
        elif 'bank america' in bank_file_lower or 'bankamerica' in bank_file_lower:
            return 'Bank of America'
        elif 'capitalone' in bank_file_lower or 'capital one' in bank_file_lower:
            return 'Capital One'
        else:
            return 'Unknown Bank'

    def get_card_number(self, df: pd.DataFrame, bank_file: str) -> str:
        if 'Card No.' in df.columns:
            return df['Card No.'].astype(str).str[-4:]
        else:
            card_number = ''.join(filter(str.isdigit, bank_file))[-4:]
            return card_number if card_number else 'Unknown'

    def apply_rules(self, df):
        return self.rules_processor.apply_rules(df)