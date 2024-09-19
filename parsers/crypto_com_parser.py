import pandas as pd

class CryptoComParser:
    def parse(self, filepath: str) -> pd.DataFrame:
        df = pd.read_csv(filepath)

        # Rename columns to standardized format
        df = df.rename(columns={
            'Timestamp (UTC)': 'datetime',
            'Transaction Description': 'vendor',
            'Currency': 'currency',
            'Amount': 'amount',
            'Native Currency': 'native_currency',
            'Native Amount': 'native_amount',
            'Transaction Kind': 'category'
        })

        # Split datetime into date and time
        df['date'] = pd.to_datetime(df['datetime']).dt.date
        df['time'] = pd.to_datetime(df['datetime']).dt.time

        # Convert amount to negative for expenses
        df['amount'] = -df['amount'].abs()

        # Add bank column
        df['bank'] = 'Crypto.com'

        # Extract card number (assuming it's in the filename)
        card_no = filepath.split('_')[-1].split('.')[0]
        df['card_no'] = card_no

        # Reorder columns
        df = df[['date', 'time', 'vendor', 'amount', 'currency', 'bank', 'card_no', 'category']]

        return df