import pandas as pd

class CapitalOneParser:
    def parse(self, filepath: str) -> pd.DataFrame:
        df = pd.read_csv(filepath)

        # Rename columns to standardized format
        df = df.rename(columns={
            'Transaction Date': 'date',
            'Posted Date': 'posted_date',
            'Card No.': 'card_no',
            'Description': 'vendor',
            'Category': 'category',
            'Debit': 'debit',
            'Credit': 'credit'
        })

        # Combine debit and credit into a single amount column
        df['amount'] = df['credit'].fillna(0) - df['debit'].fillna(0)

        # Drop original debit and credit columns
        df = df.drop(columns=['debit', 'credit'])

        # Ensure date is in correct format
        df['date'] = pd.to_datetime(df['date'])

        # Add bank column
        df['bank'] = 'Capital One'

        # Add time column (set to midnight as Capital One doesn't provide time)
        df['time'] = '00:00:00'

        # Add currency column (assuming USD)
        df['currency'] = 'USD'

        # Reorder columns
        df = df[['date', 'time', 'vendor', 'amount', 'currency', 'bank', 'card_no', 'category']]

        return df