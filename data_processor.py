# data_processor.py

import os
import pandas as pd
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class DataProcessor:
    def __init__(self, config):
        self.config = config
        self.input_files = {}

    def load_data(self):
        logger.info("Loading data from input files...")
        dfs = []
        for file in os.listdir(self.config['input_dir']):
            if file.lower().endswith('.csv'):
                file_path = os.path.join(self.config['input_dir'], file)
                logger.info(f"Processing file: {file}")
                df = pd.read_csv(file_path)
                df['Source'] = file  # Add source file information
                self.input_files[file] = list(df.columns)
                dfs.append(df)

        if not dfs:
            logger.warning("No CSV files found in the input directory.")
            return pd.DataFrame()

        merged_df = pd.concat(dfs, ignore_index=True)
        logger.info(f"Data loading complete. Merged DataFrame shape: {merged_df.shape}")
        return merged_df

    def preprocess_data(self, df):
        logger.info("Preprocessing data...")

        # Standardize column names
        df.columns = df.columns.str.lower().str.replace(' ', '_')

        # Ensure required columns exist
        required_columns = ['date', 'description', 'amount', 'category']
        for col in required_columns:
            if col not in df.columns:
                logger.error(f"Required column '{col}' not found in the data.")
                raise ValueError(f"Required column '{col}' not found in the data.")

        # Convert date to datetime
        df['date'] = pd.to_datetime(df['date'], errors='coerce')

        # Handle the 'category' column
        df['category'] = df['category'].apply(self.process_category)

        # Convert amount to float
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce')

        logger.info("Data preprocessing complete.")
        return df

    def process_category(self, category):
        if isinstance(category, pd.Series):
            return category.iloc[0] if not category.empty else 'Uncategorized'
        return category if pd.notna(category) else 'Uncategorized'

    def validate_data(self, df):
        logger.info("Validating data...")

        # Check for missing values
        missing_values = df.isnull().sum()
        if missing_values.any():
            logger.warning(f"Missing values found:\n{missing_values[missing_values > 0]}")

        # Check date range
        start_date = datetime.strptime(self.config['date_range']['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(self.config['date_range']['end_date'], '%Y-%m-%d')
        date_mask = (df['date'] >= start_date) & (df['date'] <= end_date)
        if not date_mask.all():
            logger.warning(f"Some transactions are outside the specified date range. "
                           f"Transactions within range: {date_mask.sum()} out of {len(df)}")

        # Check for negative amounts
        if (df['amount'] >= 0).any():
            logger.warning("Some transactions have non-negative amounts. Expenses should be negative.")

        logger.info("Data validation complete.")

    def process(self):
        df = self.load_data()
        df = self.preprocess_data(df)
        self.validate_data(df)
        return df

    def get_input_files(self):
        return self.input_files


if __name__ == "__main__":
    # This allows for easy testing of this module independently
    import json

    with open('config.json', 'r') as f:
        config = json.load(f)

    processor = DataProcessor(config)
    processed_data = processor.process()
    print(processed_data.head())
    print(f"Processed data shape: {processed_data.shape}")
    print(f"Input files processed: {processor.get_input_files()}")