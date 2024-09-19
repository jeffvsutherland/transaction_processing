# acceptance_tests.py

import pandas as pd
import logging
import os
import re

logger = logging.getLogger(__name__)

def test_intermediate_files_have_bank_and_card(output_dir):
    for file in os.listdir(output_dir):
        if file.startswith('intermediate_') and file.endswith('.csv'):
            df = pd.read_csv(os.path.join(output_dir, file))
            if 'Bank' not in df.columns or 'Card' not in df.columns:
                logger.error(f"File {file} is missing 'Bank' or 'Card' column")
                return False
            if df['Bank'].isnull().any() or df['Card'].isnull().any():
                logger.error(f"File {file} has null values in 'Bank' or 'Card' column")
                return False
    return True

def test_merged_transactions_have_required_columns(merged_df):
    required_columns = ['Date', 'Description', 'Amount', 'Bank', 'Card', 'employer', 'category', 'note', 'Vendor']
    missing_columns = [col for col in required_columns if col not in merged_df.columns]
    if missing_columns:
        logger.error(f"Merged transactions are missing required columns: {', '.join(missing_columns)}")
        return False
    return True

def test_vendor_column_has_no_missing_values(merged_df):
    if 'Vendor' not in merged_df.columns:
        logger.error("'Vendor' column is missing from the merged DataFrame")
        return False
    if merged_df['Vendor'].isnull().any():
        logger.error("Vendor column has missing values")
        return False
    return True

def test_vendor_column_has_no_unknown_values(merged_df):
    if 'Vendor' not in merged_df.columns:
        logger.error("'Vendor' column is missing from the merged DataFrame")
        return False
    if (merged_df['Vendor'] == 'Unknown').any():
        logger.error("Vendor column has 'Unknown' values")
        return False
    return True

def test_all_bank_files_processed(input_dir, report_details):
    input_files = set(os.listdir(input_dir))
    processed_files = set(report_details['input_files'])
    if input_files != processed_files:
        unprocessed = input_files - processed_files
        logger.error(f"The following files were not processed: {unprocessed}")
        return False
    return True

def test_amount_has_two_decimal_places(merged_df):
    if 'Amount' not in merged_df.columns:
        logger.error("'Amount' column is missing from the merged DataFrame")
        return False

    # Convert Amount to string and check for exactly two decimal places
    amounts = merged_df['Amount'].astype(str)
    invalid_amounts = amounts[~amounts.str.match(r'^\-?\d+\.\d{2}$')]

    if not invalid_amounts.empty:
        logger.error(f"The following amounts do not have exactly two decimal places: {invalid_amounts.tolist()}")
        return False
    return True

def test_manual_transactions_unchanged(output_dir, merged_df):
    manual_expenses_file = os.path.join(output_dir, 'manual_expenses.csv')
    if not os.path.exists(manual_expenses_file):
        logger.error(f"Manual expenses file not found: {manual_expenses_file}")
        return False

    manual_expenses = pd.read_csv(manual_expenses_file)
    merged_manual_expenses = merged_df[merged_df['Bank'] == 'Manual Entry']

    if len(manual_expenses) != len(merged_manual_expenses):
        logger.error(f"Number of manual expenses before ({len(manual_expenses)}) and after ({len(merged_manual_expenses)}) merge do not match")
        return False

    columns_to_check = ['Date', 'Description', 'Amount', 'employer', 'category', 'note', 'Vendor']
    for col in columns_to_check:
        if col == 'Date':
            # Convert both to datetime for comparison
            manual_dates = pd.to_datetime(manual_expenses[col]).dt.date
            merged_dates = pd.to_datetime(merged_manual_expenses[col]).dt.date
            if not manual_dates.equals(merged_dates):
                logger.error(f"Manual expenses differ in '{col}' column after merge")
                logger.error(f"Original: {manual_dates.tolist()}")
                logger.error(f"Merged: {merged_dates.tolist()}")
                return False
        elif not manual_expenses[col].equals(merged_manual_expenses[col]):
            logger.error(f"Manual expenses differ in '{col}' column after merge")
            logger.error(f"Original: {manual_expenses[col].tolist()}")
            logger.error(f"Merged: {merged_manual_expenses[col].tolist()}")
            return False

    logger.info("Manual transactions remained unchanged after merge")
    return True

def run_acceptance_tests(merged_df, input_dir, output_dir, report_details, start_date, end_date):
    tests = {
        'test_intermediate_files_have_bank_and_card': test_intermediate_files_have_bank_and_card(output_dir),
        'test_merged_transactions_have_required_columns': test_merged_transactions_have_required_columns(merged_df),
        'test_vendor_column_has_no_missing_values': test_vendor_column_has_no_missing_values(merged_df),
        'test_vendor_column_has_no_unknown_values': test_vendor_column_has_no_unknown_values(merged_df),
        'test_all_bank_files_processed': test_all_bank_files_processed(input_dir, report_details),
        'test_amount_has_two_decimal_places': test_amount_has_two_decimal_places(merged_df),
        'test_manual_transactions_unchanged': test_manual_transactions_unchanged(output_dir, merged_df),
    }

    # Print test results to console
    for test_name, result in tests.items():
        logger.info(f"{test_name}: {'Passed' if result else 'Failed'}")

    return tests

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("This script is not meant to be run directly. Please run main.py instead.")