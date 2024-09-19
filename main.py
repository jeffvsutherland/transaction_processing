# main.py

import os
import sys
import json
import logging
from datetime import datetime
import pandas as pd
from bank_data_processor import BankDataProcessor
from generate_final_report import save_final_report
from acceptance_tests import run_acceptance_tests
from rules_processor import RulesProcessor

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
#logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_json(file_path):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from {file_path}: {str(e)}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error loading JSON from {file_path}: {str(e)}")
        sys.exit(1)

def save_merged_transactions(merged_df, output_dir):
    merged_file = os.path.join(output_dir, 'merged_transactions.csv')
    columns_to_save = ['Date', 'Description', 'Amount', 'Bank', 'Card', 'employer', 'category', 'note', 'Vendor']

    # Format Amount to always have two decimal places
    merged_df['Amount'] = merged_df['Amount'].apply(lambda x: f"{float(x):.2f}")

    merged_df[columns_to_save].to_csv(merged_file, index=False)
    logger.info(f"Merged transactions saved to: {merged_file}")
    logger.info(f"Number of transactions saved: {len(merged_df)}")

def save_unknown_transactions(merged_df, output_dir):
    unknown_df = merged_df[merged_df['employer'] == 'Unknown']
    if not unknown_df.empty:
        unknown_file = os.path.join(output_dir, 'unknown_transactions.csv')
        columns_to_save = ['Date', 'Description', 'Amount', 'Bank', 'Card', 'employer', 'category', 'note', 'Vendor']
        unknown_df[columns_to_save].to_csv(unknown_file, index=False)
        logger.info(f"Unknown transactions saved to: {unknown_file}")
        logger.info(f"Number of unknown transactions: {len(unknown_df)}")
    else:
        logger.info("No unknown transactions found.")

def load_manual_transactions(output_dir):
    manual_expenses_file = os.path.join(output_dir, 'manual_expenses.csv')
    if os.path.exists(manual_expenses_file):
        df = pd.read_csv(manual_expenses_file, parse_dates=['Date'])
        df['Bank'] = 'Manual Entry'  # Ensure 'Bank' column exists and is set to 'Manual Entry'
        return df
    else:
        logger.warning(f"Manual expenses file not found: {manual_expenses_file}")
        return pd.DataFrame()

def process_category_column(series):
    def process_category(x):
        if isinstance(x, pd.Series):
            return x.iloc[0] if not x.empty else 'Uncategorized'
        return x if pd.notna(x) else 'Uncategorized'

    return series.apply(process_category)

def main():
    # Load configuration
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, 'config.json')
    categories_path = os.path.join(base_dir, 'categories.json')
    config = load_json(config_path)
    categories = load_json(categories_path)

    # Ensure output directory exists
    os.makedirs(config['output_dir'], exist_ok=True)

    # Initialize RulesProcessor
    rules_processor = RulesProcessor(config_path, categories_path)

    # Initialize BankDataProcessor
    processor = BankDataProcessor(config['input_dir'], config['output_dir'], rules_processor)

    # Process files
    start_date = datetime.strptime(config['date_range']['start_date'], '%Y-%m-%d')
    end_date = datetime.strptime(config['date_range']['end_date'], '%Y-%m-%d')
    intermediate_files, input_files = processor.process_bank_files(start_date, end_date)

    # Load manual transactions
    manual_transactions = load_manual_transactions(config['output_dir'])

    # Merge processed files
    all_dfs = list(intermediate_files.values())
    if all_dfs or not manual_transactions.empty:
        if all_dfs:
            merged_df = pd.concat(all_dfs, ignore_index=True)
            if not manual_transactions.empty:
                merged_df = pd.concat([merged_df, manual_transactions], ignore_index=True)
        else:
            merged_df = manual_transactions

        logger.info(f"Merged transactions. Total transactions: {len(merged_df)}")

        # Check for manual transactions
        manual_transactions_in_merged = merged_df[merged_df['Bank'] == 'Manual Entry']
        logger.info(f"Number of manual transactions: {len(manual_transactions_in_merged)}")
        if not manual_transactions_in_merged.empty:
            logger.info("Manual transactions found:")
            logger.info(manual_transactions_in_merged.to_string())
        else:
            logger.warning("No manual transactions found in merged data.")

        # Ensure all necessary columns exist
        for col in ['employer', 'category', 'note', 'Vendor']:
            if col not in merged_df.columns:
                merged_df[col] = 'Unknown'
                logger.warning(f"Added missing column '{col}' to merged DataFrame")

        # If 'Vendor' column is missing or has 'Unknown' values, use 'Description' as 'Vendor'
        if 'Vendor' not in merged_df.columns or (merged_df['Vendor'] == 'Unknown').any():
            merged_df.loc[merged_df['Vendor'] == 'Unknown', 'Vendor'] = merged_df['Description']
            logger.info("Updated 'Vendor' column with values from 'Description' column where it was 'Unknown'")

        # Format Amount to always have two decimal places
        merged_df['Amount'] = merged_df['Amount'].apply(lambda x: f"{float(x):.2f}")

        # Apply rules to merged transactions, but not to manual transactions
        non_manual_mask = merged_df['Bank'] != 'Manual Entry'
        merged_df.loc[non_manual_mask] = rules_processor.apply_rules(merged_df[non_manual_mask])

        # Process the category column, but not for manual transactions
        merged_df.loc[non_manual_mask, 'category'] = process_category_column(merged_df.loc[non_manual_mask, 'category'])

        # Save merged transactions
        save_merged_transactions(merged_df, config['output_dir'])

        # Save unknown transactions
        save_unknown_transactions(merged_df, config['output_dir'])

        # Run acceptance tests
        acceptance_test_results = run_acceptance_tests(
            merged_df,
            config['input_dir'],
            config['output_dir'],
            {'input_files': input_files},
            start_date,
            end_date
        )
    else:
        logger.warning(
            "No intermediate files were created and no manual transactions found. Unable to generate merged transactions or run acceptance tests.")
        merged_df = pd.DataFrame()
        acceptance_test_results = {}

    data = {
        'input_files': input_files,
        'intermediate_files': intermediate_files,
        'merged_df': merged_df,
        'py_files': [f for f in os.listdir(base_dir) if f.endswith('.py')],
        'acceptance_test_results': acceptance_test_results
    }

    # Generate and save final report
    report_md_path, report_pdf_path, report_content = save_final_report(
        data,
        processor.errors,
        start_date,
        end_date,
        config['output_dir'],
        base_dir
    )

    # Print final report
    print("\n--- Final Report ---\n")
    print(report_content)
    print("\n--- End of Final Report ---\n")

    logger.info(f"Final report saved to: {report_md_path}")
    if report_pdf_path:
        logger.info(f"PDF report saved to: {report_pdf_path}")
    else:
        logger.info("PDF report could not be generated. Please refer to the Markdown file.")

    if processor.errors:
        logger.error("Processing completed with errors.")
        for error in processor.errors:
            logger.error(f"Error: {error}")
    else:
        logger.info("Processing completed successfully.")

if __name__ == "__main__":
    main()