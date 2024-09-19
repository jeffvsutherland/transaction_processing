# transaction_merger.py

import os
import pandas as pd
from typing import Dict
import logging

class TransactionMerger:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.logger = logging.getLogger(__name__)

    def merge_transactions(self, intermediate_files: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        if not intermediate_files:
            self.logger.warning("No intermediate files to merge.")
            return pd.DataFrame()

        merged_df = pd.concat(intermediate_files.values(), ignore_index=True)

        if merged_df.empty:
            self.logger.warning("Merged DataFrame is empty.")
            return merged_df

        self.logger.info(f"Merged DataFrame columns: {merged_df.columns.tolist()}")

        # Check for 'Normalized Date' column
        if "Normalized Date" not in merged_df.columns:
            self.logger.warning("'Normalized Date' is not a column of the DataFrame. Attempting to use 'date' column.")
            if 'date' in merged_df.columns:
                merged_df['Normalized Date'] = pd.to_datetime(merged_df['date'])
            else:
                self.logger.error("Neither 'Normalized Date' nor 'date' column found. Unable to sort transactions.")
                return merged_df

        # Sort the DataFrame
        try:
            merged_df.sort_values('Normalized Date', inplace=True)
            self.logger.info("Successfully sorted merged DataFrame by 'Normalized Date'.")
        except KeyError as e:
            self.logger.error(f"Error sorting DataFrame: {str(e)}")
        except Exception as e:
            self.logger.error(f"Unexpected error during sorting: {str(e)}")

        output_path = os.path.join(self.output_dir, 'merged_transactions.csv')
        merged_df.to_csv(output_path, index=False)
        self.logger.info(f"Merged transactions saved to {output_path}")

        return merged_df

if __name__ == "__main__":
    # This block is for testing purposes
    import json

    base_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base_dir, 'config.json'), 'r') as f:
        config = json.load(f)

    merger = TransactionMerger(os.path.join(base_dir, config['output_dir']))

    # You would need to provide some sample intermediate files for testing
    # intermediate_files = {...}
    # merged_df = merger.merge_transactions(intermediate_files)
    # print(merged_df.head())