import os
import pandas as pd
from datetime import datetime
from acceptance_tests import run_acceptance_tests
from create_merged_files import create_final_merged_file, save_merged_file

def log(message, log_file='logfile.log'):
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        formatted_message = f"[{timestamp}] {message}"
        print(formatted_message)
        with open(log_file, 'a') as f:
            f.write(formatted_message + '\n')
    except Exception as e:
        print(f"Logging error: {e}")

def find_date_column(df):
    possible_date_columns = ['Timestamp (UTC)', 'Transaction Date', 'DATE']
    for column in possible_date_columns:
        if column in df.columns:
            df['Normalized Date'] = pd.to_datetime(df[column])
            return 'Normalized Date'
    raise ValueError("No valid date column found in the data.")

def process_bank_file(filepath, config, output_dir, start_date, end_date):
    bank_name = os.path.basename(filepath)
    log(f"Processing file: {bank_name}")

    df = pd.read_csv(filepath)
    log(f"Available columns in {bank_name}: {list(df.columns)}")

    try:
        date_column = find_date_column(df)
        df = df[(df[date_column] >= start_date) & (df[date_column] <= end_date)]

        if 'bank of america' in bank_name.lower():
            df['Bank'] = 'Bank of America'
            df['Card'] = bank_name.split('_')[-1][:4]
        elif 'chase' in bank_name.lower():
            df['Bank'] = 'Chase'
            df['Card'] = bank_name.split('_')[-1][:4]
        elif 'crypto.com' in bank_name.lower():
            df['Bank'] = 'Crypto.com'
            df['Card'] = bank_name.split('_')[-1][:4]
        else:
            df['Bank'] = bank_name
            if 'Card No.' in df.columns:
                df['Card'] = df['Card No.'].astype(str).apply(lambda x: x[-4:])
                log(f"Extracted card number: {df['Card'].unique()}")
            else:
                df['Card'] = 'Unknown'

        if 'Card Last Four' in df.columns:
            df.drop(columns=['Card Last Four'], inplace=True)

        intermediate_file_path = os.path.join(output_dir, f"intermediate_{bank_name}")
        df.to_csv(intermediate_file_path, index=False)
        log(f"Intermediate file saved at: {intermediate_file_path}")

        return df
    except Exception as e:
        log(f"Error processing {bank_name}: {str(e)}")
        return None

def create_intermediate_files(config, start_date, end_date):
    intermediate_files = {}
    input_files = {}
    for bank_file in os.listdir(config['input_dir']):
        if bank_file.lower().endswith('.csv'):
            filepath = os.path.join(config['input_dir'], bank_file)
            df = process_bank_file(filepath, config, config['output_dir'], start_date, end_date)
            if df is not None:
                intermediate_files[bank_file] = df
                input_files[bank_file] = list(df.columns)
            else:
                log(f"Failed to process file: {bank_file}")
    return intermediate_files, input_files

def merge_transactions(config, start_date, end_date):
    report_details = {
        'overview': """This is an application designed to process bank transaction files and generate expense reports. The application reads bank files, processes transactions within a specified date range, merges the transactions, and generates a final report in markdown format. The final report includes an overview, status, working directory structure, input files, intermediate files, merged transactions, expense reports for each employer, and a console log.""",
        'status': "",
        'working_directory': get_directory_structure(config['input_dir']),
        'input_files': {},
        'intermediate_files': {},
        'merged_transactions': pd.DataFrame(),
        'expense_reports': {},
        'console_log': "",
        'acceptance_tests': {}
    }

    intermediate_files, input_files = create_intermediate_files(config, start_date, end_date)
    report_details['intermediate_files'] = intermediate_files
    report_details['input_files'] = input_files

    intermediate_dir = config['output_dir']
    output_path = os.path.join(config['output_dir'], 'merged_transactions.csv')
    merged_df = create_final_merged_file(intermediate_dir, output_path)
    save_merged_file(merged_df, output_path)

    if os.path.exists(output_path):
        merged_df = pd.read_csv(output_path)
        report_details['merged_transactions'] = merged_df

        acceptance_test_results = run_acceptance_tests(merged_df, config['input_dir'], config['output_dir'], {'input_files': input_files})
        report_details['acceptance_tests'] = acceptance_test_results

    return report_details