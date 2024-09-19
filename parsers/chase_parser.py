import pandas as pd

class ChaseParser:
    def parse(self, filepath: str) -> pd.DataFrame:
        df = pd.read_csv(filepath)

        # Rename columns to standardized format
        df = df.rename(columns={
            'Transaction Date': 'date',
            'Post Date': 'posted_date',
            'Description': 'vendor',
            'Category': 'category',
            'Type': 'transaction_type',
            'Amount': 'amount',
            'Memo': 'memo'
        })

        # Ensure date is in correct format
        df['date'] = pd.to_datetime(df['date'])

        # Convert amount to negative for expenses
        df['amount'] = -df['amount'].abs()

        # Add bank column
        df['bank'] = 'Chase'

        # Add time column (set to midnight as Chase doesn't provide time)
        df['time'] = '00:00:00'

        # Add currency column (assuming USD)
        df['currency'] = 'USD'

        # Extract card number (assuming it's in the filename)
        card_no = filepath.split('_')[-1].split('.')[0]
        df['card_no'] = card_no

        # Reorder columns
        df = df[['date', 'time', 'vendor', 'amount', 'currency', 'bank', 'card_no', 'category']]

        return df