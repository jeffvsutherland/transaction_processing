import pandas as pd
from datetime import datetime
from typing import Tuple

class DateProcessor:
    def __init__(self):
        self.possible_date_columns = ['Timestamp', 'Timestamp (UTC)', 'Transaction Date', 'DATE', 'Date', 'date']

    def process(self, df: pd.DataFrame, date_column: str) -> pd.DataFrame:
        df['Normalized Date'] = pd.to_datetime(df[date_column])
        df['date'] = df['Normalized Date'].dt.date
        df['time'] = df['Normalized Date'].dt.time
        return df

    def find_date_column(self, df: pd.DataFrame) -> str:
        for column in self.possible_date_columns:
            if column in df.columns:
                return column
        
        # If no exact match found, try case-insensitive matching
        lowercase_columns = [col.lower() for col in df.columns]
        for column in self.possible_date_columns:
            if column.lower() in lowercase_columns:
                return df.columns[lowercase_columns.index(column.lower())]
        
        raise ValueError("No valid date column found in the data.")
