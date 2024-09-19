import pandas as pd
import logging
from datetime import datetime
import traceback
import json
import os

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_config(config_path):
    with open(config_path, 'r') as f:
        return json.load(f)


def load_notes(notes_path):
    with open(notes_path, 'r') as f:
        return json.load(f)


def generate_employer_expense_report(df, employer, config, notes, start_date, end_date):
    logger.debug(f"DataFrame shape at start of function: {df.shape}")
    logger.debug(f"DataFrame columns: {df.columns}")
    logger.debug(f"Unique values in 'category' column: {df['category'].unique()}")
    logger.debug(f"Unique values in 'employer' column: {df['employer'].unique()}")
    logger.debug(f"Data types of DataFrame columns:\n{df.dtypes}")

    submitter_name = config.get('submitter_name', 'Unknown Submitter')
    date_range = f"{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}"
    report = f"# {date_range}_{employer} Expense Report\n"
    report += f"## {submitter_name} - {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}\n\n"

    # Get travel days from config
    travel_days = []
    for employee_rule in config.get('employee_rules', []):
        if employee_rule['name'] == submitter_name:
            travel_days = employee_rule.get('travel_days', [])
            break

    logger.debug(f"Travel days: {travel_days}")

    # Convert travel_days to datetime for comparison
    travel_days = pd.to_datetime(travel_days)

    # Ensure 'Date' column is datetime
    df['Date'] = pd.to_datetime(df['Date'])

    # Filter for the specific employer
    df_employer = df[df['employer'] == employer].copy()
    logger.debug(f"Employer-specific DataFrame shape: {df_employer.shape}")

    # Handle travel day food expenses
    travel_employer = config.get('travel_employer', 'Frequency Research Foundation')
    if employer == travel_employer:
        mask_date = df['Date'].isin(travel_days)
        logger.debug(f"Date mask shape: {mask_date.shape}, True count: {mask_date.sum()}")

        mask_category = (df['category'] == 'Food')
        logger.debug(f"Category mask shape: {mask_category.shape}, True count: {mask_category.sum()}")

        mask_employer = (df['employer'] != employer)
        logger.debug(f"Employer mask shape: {mask_employer.shape}, True count: {mask_employer.sum()}")

        travel_food_df = df[mask_date & mask_category & mask_employer]

        logger.debug(f"Travel food expenses shape: {travel_food_df.shape}")
        if not travel_food_df.empty:
            df_employer = pd.concat([df_employer, travel_food_df])
            logger.debug(f"Combined DataFrame shape: {df_employer.shape}")

    # Sort the DataFrame
    df_employer = df_employer.sort_values(['category', 'Date'])

    # Convert 'Amount' to string with two decimal places
    df_employer['Amount'] = df_employer['Amount'].apply(lambda x: f"{float(x):.2f}")

    logger.debug(f"Final DataFrame shape: {df_employer.shape}")
    logger.debug(f"Final DataFrame columns: {df_employer.columns}")

    return report


def main():
    try:
        # Load configuration and notes
        config_path = 'config.json'
        notes_path = 'note.json'
        merged_transactions_path = 'output/merged_transactions.csv'

        config = load_config(config_path)
        notes = load_notes(notes_path)

        # Load merged transactions
        df = pd.read_csv(merged_transactions_path)
        logger.info(f"Loaded {len(df)} transactions from {merged_transactions_path}")

        # Set date range
        start_date = datetime.strptime(config['date_range']['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(config['date_range']['end_date'], '%Y-%m-%d')

        # Generate report for each employer
        for employer in config['employers']:
            logger.info(f"Generating report for {employer}")
            report = generate_employer_expense_report(df, employer, config, notes, start_date, end_date)
            logger.info(f"Report generated for {employer}")

        logger.info("All reports generated successfully")

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        logger.error(f"Full traceback:\n{traceback.format_exc()}")


if __name__ == "__main__":
    main()