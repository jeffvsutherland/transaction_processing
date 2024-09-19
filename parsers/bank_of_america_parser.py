import pandas as pd
import logging

class BankOfAmericaParser:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def parse(self, filepath: str) -> pd.DataFrame:
        try:
            df = pd.read_csv(filepath)
            self.logger.info(f"Successfully read CSV file: {filepath}")
            self.logger.info(f"Columns in the CSV: {df.columns.tolist()}")

            # Rename columns to standardized format
            df = df.rename(columns={
                'DATE': 'date',  # Changed from 'Date' to 'DATE'
                'DESCRIPTION': 'vendor',  # Changed from 'Description' to 'DESCRIPTION'
                'AMOUNT': 'amount'  # Changed from 'Amount' to 'AMOUNT'
            })

            # Ensure date is in correct format
            df['date'] = pd.to_datetime(df['date'])

            # Convert amount to negative for expenses
            df['amount'] = -df['amount'].abs()

            # Add bank column
            df['bank'] = 'Bank of America'

            # Add time column (set to midnight as Bank of America doesn't provide time)
            df['time'] = '00:00:00'

            # Add currency column (assuming USD)
            df['currency'] = 'USD'

            # Extract card number (assuming it's in the filename)
            card_no = filepath.split('_')[-1].split('.')[0]
            df['card_no'] = card_no

            # Add category column (Bank of America might not provide this)
            df['category'] = 'Uncategorized'

            # Add employer column (to be filled later)
            df['employer'] = ''

            # Add note column
            df['note'] = ''

            # Reorder columns
            df = df[['date', 'time', 'vendor', 'amount', 'currency', 'bank', 'card_no', 'employer', 'category', 'note']]

            self.logger.info(f"Successfully parsed Bank of America file. Shape: {df.shape}")
            return df
        except Exception as e:
            self.logger.error(f"Error parsing Bank of America file: {str(e)}", exc_info=True)
            raise