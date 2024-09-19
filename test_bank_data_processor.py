import os
import pandas as pd
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DateProcessor:
    def __init__(self):
        self.possible_date_columns = ['Timestamp (UTC)', 'Transaction Date', 'DATE', 'Posted Date', 'Post Date']

    def find_date_column(self, df):
        for col in self.possible_date_columns:
            if col in df.columns:
                return col
        raise ValueError("No date column found")

    def process(self, df, date_column):
        if date_column == 'Timestamp (UTC)':
            df['Date'] = pd.to_datetime(df[date_column]).dt.date
            df['Time'] = pd.to_datetime(df[date_column]).dt.time
        else:
            df['Date'] = pd.to_datetime(df[date_column]).dt.date
            df['Time'] = pd.to_datetime(df[date_column]).dt.time.fillna('00:00:00')
        df['Normalized Date'] = pd.to_datetime(df[date_column])
        return df

def get_bank_name(bank_file: str) -> str:
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

def get_card_number(df: pd.DataFrame, bank_file: str) -> str:
    if 'Card No.' in df.columns:
        return df['Card No.'].astype(str).str[-4:]
    else:
        card_number = ''.join(filter(str.isdigit, bank_file))[-4:]
        return card_number if card_number else 'Unknown'

class BankDataProcessor:
    def __init__(self):
        self.date_processor = DateProcessor()

    def process_bank_file(self, filepath, bank_type, bank_file, start_date, end_date):
        df = pd.read_csv(filepath)
        logger.info(f"Original columns in {bank_file}: {df.columns.tolist()}")
        logger.info(f"Original shape: {df.shape}")

        df = self.map_description_column(df, bank_type, bank_file)
        if df is None:
            return None

        if 'Description' not in df.columns:
            logger.error(f"'Description' column is missing after mapping in {bank_file}. Cannot proceed.")
            return None

        date_column = self.date_processor.find_date_column(df)
        logger.info(f"Identified date column: {date_column}")

        df = self.date_processor.process(df, date_column)
        logger.info(f"Columns after date processing: {df.columns.tolist()}")

        df = df[(df['Normalized Date'].dt.date >= start_date.date()) & (df['Normalized Date'].dt.date <= end_date.date())]
        logger.info(f"Shape after date filtering: {df.shape}")

        # Add bank column
        df['Bank'] = get_bank_name(bank_file)
        logger.info(f"Added 'Bank' column. Unique values: {df['Bank'].unique()}")

        # Add card column with last four digits
        df['Card'] = get_card_number(df, bank_file)
        logger.info(f"Added 'Card' column. Unique values: {df['Card'].unique()}")

        logger.info(f"Final columns: {df.columns.tolist()}")
        logger.info(f"Final shape: {df.shape}")
        logger.info(f"Processed data from {bank_file}:\n{df.head()}")

        return df

    def map_description_column(self, df, bank_type, bank_file):
        if 'Description' not in df.columns:
            if bank_type == 'crypto_com' and 'Transaction Description' in df.columns:
                df['Description'] = df['Transaction Description']
            elif bank_type == 'bank_of_america' and 'DESCRIPTION' in df.columns:
                df['Description'] = df['DESCRIPTION']
            else:
                logger.error(f"Error processing {bank_file}: 'Description' or equivalent column not found.")
                logger.info(f"Available columns: {df.columns.tolist()}")
                return None

        if 'Description' not in df.columns:
            logger.error(f"Error: 'Description' column missing even after mapping in {bank_file}.")
            return None

        logger.info(f"'Description' column successfully mapped for bank type '{bank_type}'.")
        return df

if __name__ == "__main__":
    # Test directory setup
    test_input_dir = '/Users/jeffsutherland/Frequency Research Foundation Inc. Dropbox/Frequency Lab/Python/Expenses/chatGPT4o scripts/transaction_processor/input'
    test_output_dir = '/Users/jeffsutherland/Frequency Research Foundation Inc. Dropbox/Frequency Lab/Python/Expenses/chatGPT4o scripts/transaction_processor/output'
    os.makedirs(test_output_dir, exist_ok=True)

    processor = BankDataProcessor()

    # Test files and their corresponding bank types
    test_files = [
        ('2022 crypto_com visa card 7712.csv', 'crypto_com'),
        ('2022 Bank America visa 0596.csv', 'bank_of_america'),
        ('2022 Chase visa 3785.csv', 'chase'),
        ('2022 capitalone VISA.csv', 'capital_one')
    ]

    start_date = datetime(2022, 10, 26)
    end_date = datetime(2022, 10, 27)

    for bank_file, bank_type in test_files:
        logger.info(f"\nProcessing file: {bank_file}")
        filepath = os.path.join(test_input_dir, bank_file)
        df = processor.process_bank_file(filepath, bank_type, bank_file, start_date, end_date)
        if df is not None:
            logger.info(f"Final DataFrame for {bank_file}:\n{df.head()}")
            output_file = os.path.join(test_output_dir, f"test_output_{bank_file}")
            df.to_csv(output_file, index=False)
            logger.info(f"Saved processed file to: {output_file}")
        else:
            logger.error(f"Failed to process {bank_file}.")