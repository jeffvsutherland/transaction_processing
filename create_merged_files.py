import os
import pandas as pd
from datetime import datetime

def log(message, log_file='logfile.log'):
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        formatted_message = f"[{timestamp}] {message}"
        print(formatted_message)
        with open(log_file, 'a') as f:
            f.write(formatted_message + '\n')
    except Exception as e:
        print(f"Logging error: {e}")

def create_final_merged_file(merged_df, output_dir):
    final_file_path = os.path.join(output_dir, 'final_merged_file.csv')
    merged_df.to_csv(final_file_path, index=False)
    log(f"Final merged file created at: {final_file_path}")
    return final_file_path

def save_merged_file(merged_df, output_dir):
    merged_file_path = os.path.join(output_dir, 'merged_transactions.csv')
    merged_df.to_csv(merged_file_path, index=False)
    log(f"Merged file saved at: {merged_file_path}")
    return merged_file_path

def generate_final_report(report_details, output_dir):
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    report_file = os.path.join(output_dir, f"final_report_{timestamp}.md")

    with open(report_file, 'w') as f:
        f.write(f"# Expense Report - {timestamp}\n\n")
        f.write("## Expense report product overview\n")
        f.write(report_details['overview'])

        f.write("\n## Status: Known bugs or failures in this cycle\n")
        f.write(report_details['status'])

        f.write("\n## Working Directory Structure\n")
        f.write(report_details['working_directory'])

        f.write("\n## Input: List of bank files accessed with their column structure\n")
        for bank_file, columns in report_details['input_files'].items():
            f.write(f"- **{bank_file}**: {', '.join(columns)}\n")

        f.write("\n## Processing\n")
        f.write("### Intermediate Files\n")
        for bank_file, df in report_details['intermediate_files'].items():
            f.write(f"#### {bank_file}\n")
            f.write(df.to_markdown())

        f.write("\n### Merged Transactions\n")
        f.write(report_details['merged_transactions'].to_markdown())

        f.write("\n## Output: Expense Reports\n")
        for employer, report in report_details['expense_reports'].items():
            f.write(f"### {employer}\n")
            f.write(report.to_markdown())

        f.write("\n## Console Log\n")
        f.write(report_details['console_log'])

        f.write("\n## Acceptance Tests\n")
        for test, result in report_details['acceptance_tests'].items():
            f.write(f"- **{test}**: {'Passed' if result else 'Failed'}\n")

        f.write("\n## Scripts and JSON Files\n")
        for script in report_details['scripts_and_json_files']:
            f.write(f"- {script}\n")

    log(f"Final report generated at: {report_file}")

def get_directory_structure(rootdir):
    dir_structure = {}
    for dirpath, dirnames, filenames in os.walk(rootdir):
        folder = os.path.basename(dirpath)
        dir_structure[folder] = {'files': filenames, 'subfolders': dirnames}
    return dir_structure

def run_acceptance_tests(merged_df, input_dir, output_dir, report_details):
    tests = {
        "Required Columns Present": all(col in merged_df.columns for col in ['Normalized Date', 'Vendor', 'Amount', 'Currency', 'Bank', 'Card Last Four', 'Employer', 'Note']),
        "Non-Empty DataFrame": not merged_df.empty,
        "Valid Date Range": merged_df['Normalized Date'].between(report_details['start_date'], report_details['end_date']).all()
    }
    return tests

def merge_transactions(config, start_date, end_date):
    merged_df = pd.DataFrame()
    report_details = {
        'overview': """This is an application designed to process bank transaction files and generate expense reports. The application reads bank files, processes transactions within a specified date range, merges the transactions, and generates a final report in markdown format. The final report includes an overview, status, working directory structure, input files, intermediate files, merged transactions, expense reports for each employer, and a console log.""",
        'status': "",
        'working_directory': get_directory_structure(config['input_dir']),
        'input_files': {},
        'intermediate_files': {},
        'merged_transactions': pd.DataFrame(),
        'expense_reports': {},
        'console_log': "",
        'acceptance_tests': {},
        'start_date': start_date,
        'end_date': end_date
    }

    for bank_file in os.listdir(config['input_dir']):
        filepath = os.path.join(config['input_dir'], bank_file)
        df = pd.read_csv(filepath)

        if df is not None:
            df = df[(df['Normalized Date'] >= start_date) & (df['Normalized Date'] <= end_date)]
            report_details['input_files'][bank_file] = list(df.columns)
            report_details['intermediate_files'][bank_file] = df
            merged_df = pd.concat([merged_df, df], ignore_index=True)

    if merged_df.empty:
        log("Error during merging transactions: No transactions were processed successfully.")
    else:
        for col in ['Normalized Date', 'Vendor', 'Amount', 'Currency', 'Bank', 'Card Last Four', 'Employer', 'Note']:
            if col not in merged_df.columns:
                merged_df[col] = 'Unknown'

        selected_columns = ['Normalized Date', 'Vendor', 'Amount', 'Currency', 'Bank', 'Card Last Four', 'Employer', 'Note']
        merged_df = merged_df[selected_columns]
        report_details['merged_transactions'] = merged_df
        log(f"Transactions merged successfully. Output saved to {config['output_dir']}/merged_transactions.csv")
        merged_df.to_csv(os.path.join(config['output_dir'], 'merged_transactions.csv'), index=False)

        report_details['acceptance_tests'] = run_acceptance_tests(merged_df, config['input_dir'], config['output_dir'], report_details)

    generate_final_report(report_details, config['output_dir'])