import pandas as pd

class DateProcessor:
    def __init__(self):
        self.possible_date_columns = ['Timestamp', 'Timestamp (UTC)', 'Transaction Date', 'DATE', 'Date']

    def process(self, df: pd.DataFrame, date_column: str) -> pd.DataFrame:
        df['Normalized Date'] = pd.to_datetime(df[date_column])
        df['date'] = df['Normalized Date'].dt.date
        df['time'] = df['Normalized Date'].dt.time
        return df

    def find_date_column(self, df: pd.DataFrame) -> str:
        for column in self.possible_date_columns:
            if column in df.columns:
                return column
        raise ValueError("No valid date column found in the data.")