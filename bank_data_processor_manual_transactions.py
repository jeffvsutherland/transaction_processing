# bank_data_processor_manual_transactions.py

import pandas as pd
import logging

logger = logging.getLogger(__name__)


def load_manual_expenses(file_path):
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        logger.error(f"Error loading manual expenses from {file_path}: {str(e)}")
        return pd.DataFrame()


def merge_manual_transactions(merged_df, manual_expenses_path):
    manual_expenses = load_manual_expenses(manual_expenses_path)

    if not manual_expenses.empty:
        logger.info("Manual transactions before merge:")
        logger.info(manual_expenses.to_string())

        # Ensure all columns from manual_expenses are in merged_df
        for col in manual_expenses.columns:
            if col not in merged_df.columns:
                merged_df[col] = ''

        # Append manual expenses to merged_df
        merged_df = pd.concat([merged_df, manual_expenses], ignore_index=True)

        logger.info(f"Added {len(manual_expenses)} manual expenses. New total: {len(merged_df)}")

        logger.info("Manual transactions after merge:")
        logger.info(merged_df[merged_df['Bank'] == 'Manual Entry'].to_string())
    else:
        logger.info("No manual expenses found to merge.")

    return merged_df