# generate_final_report.py

import os
import json
import sys
from io import StringIO
from datetime import datetime
import pandas as pd
import subprocess
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Check if Pandoc is installed
try:
    subprocess.run(["pandoc", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    PDF_GENERATION_AVAILABLE = True
except (subprocess.CalledProcessError, FileNotFoundError):
    logger.warning("Pandoc is not installed. PDF generation will not be available.")
    logger.info("To install Pandoc, please visit: https://pandoc.org/installing.html")
    logger.info("Reports will be generated in Markdown format only.")
    PDF_GENERATION_AVAILABLE = False

def convert_markdown_to_pdf(input_md_path, output_pdf_path):
    try:
        subprocess.run(["pandoc", input_md_path, "-o", output_pdf_path], check=True)
        logger.info(f"PDF successfully created at {output_pdf_path}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error converting Markdown to PDF: {e}")
        raise

def load_product_description(working_dir):
    desc_path = os.path.join(working_dir, 'product_description.md')
    try:
        with open(desc_path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        logger.warning(f"Product description not found at {desc_path}")
        return "Product description not found."

def load_notes(working_dir):
    notes_path = os.path.join(working_dir, 'note.json')
    try:
        with open(notes_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"Notes file not found: {notes_path}")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON in {notes_path}: {str(e)}")
        return {}

def generate_markdown_table(df, columns):
    header = "| " + " | ".join(columns) + " |"
    separator = "|" + "|".join([":---" if col != 'Amount' else "---:" for col in columns]) + "|"
    rows = []
    for _, row in df.iterrows():
        row_str = "| " + " | ".join(str(row[col]) for col in columns) + " |"
        rows.append(row_str)
    return "\n".join([header, separator] + rows)


def generate_employer_expense_report(df, employer, config, notes, start_date, end_date):
    logger.debug(f"DataFrame shape at start of function: {df.shape}")
    logger.debug(f"DataFrame columns: {df.columns}")
    logger.debug(f"Unique values in 'category' column: {df['category'].unique()}")
    logger.debug(f"Data types of DataFrame columns:\n{df.dtypes}")

    submitter_name = config.get('submitter_name', 'Unknown Submitter')
    date_range = f"{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}"
    report = f"# {date_range}_{employer} Expense Report\n"
    report += f"## {submitter_name} - {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}\n\n"
    report += "### Created by QuickAIReports.com, a wholly owned subsidiary of JVS Management Inc.\n\n"

    # Get travel days from config
    travel_days = []
    for employee_rule in config.get('employee_rules', []):
        if employee_rule['name'] == submitter_name:
            travel_days = employee_rule.get('travel_days', [])
            break

    logger.debug(f"Travel days: {travel_days}")

    # Convert travel_days to datetime for comparison
    travel_days = pd.to_datetime(travel_days)

    # Filter for the specific employer
    df_employer = df[df['employer'] == employer].copy()
    logger.debug(f"Employer-specific DataFrame shape: {df_employer.shape}")

    # Handle travel day food expenses
    travel_employer = config.get('travel_employer', 'Frequency Research Foundation')
    if employer == travel_employer:
        travel_food_df = df[
            (df['Date'].isin(travel_days)) &
            (df['category'] == 'Food') &
            (df['employer'] != employer)
            ]
        if not travel_food_df.empty:
            logger.debug(f"Travel food expenses found. Shape: {travel_food_df.shape}")
            df_employer = pd.concat([df_employer, travel_food_df])
            logger.debug(f"Travel food expenses added. New shape: {df_employer.shape}")
        else:
            logger.debug("No travel food expenses found.")

    # Filter out rows where 'employer' is 'Unknown'
    df_employer = df_employer[df_employer['employer'] != 'Unknown']
    logger.debug(f"DataFrame shape after removing 'Unknown' employer: {df_employer.shape}")

    # Convert 'Date' column to datetime if it's not already
    if df_employer['Date'].dtype != 'datetime64[ns]':
        df_employer['Date'] = pd.to_datetime(df_employer['Date'], errors='coerce')

    # Sort the DataFrame
    df_employer = df_employer.sort_values(['category', 'Date'])

    df_employer['Amount'] = pd.to_numeric(df_employer['Amount'], errors='coerce').apply(lambda x: f"{x:.2f}")

    if df_employer.empty:
        report += "No transactions found for this employer.\n\n"
        logger.warning(f"No transactions found for employer: {employer}")
    else:
        # Calculate total amount
        total_amount = df_employer['Amount'].astype(float).sum()
        positive_amount = abs(total_amount)

        # Add "Please pay" amount at the top
        report += f"## Please pay: ${positive_amount:.2f}\n\n"

        grouped = df_employer.groupby('category')
        for category, group in grouped:
            report += f"## {category}\n\n"
            columns = ['Date', 'Description', 'Amount', 'Bank', 'Card']

            # Check if 'note' column exists and has non-empty values
            if 'note' in group.columns and group['note'].notna().any() and (group['note'].astype(str) != '').any():
                columns.append('note')

            report += generate_markdown_table(group, columns)
            report += "\n\n"
            category_total = group['Amount'].astype(float).sum()
            report += f"Category Total: ${category_total:.2f}\n\n"

        report += f"## Total Amount Debited to Employee's Accounts on Behalf of Employer: ${total_amount:.2f}\n\n"
        report += f"# Please pay: ${positive_amount:.2f}\n\n"

    # Add reimbursement information
    reimbursement_info = config.get('reimbursement_info', {})
    report += "## Reimbursement Information\n\n"
    for key, value in reimbursement_info.items():
        report += f"{key.replace('_', ' ').title()}: {value}\n"

    report += "\n## Notes\n\n"
    for note in notes.get('notes', []):
        report += f"- {note}\n"

    # Add timestamp of creation
    creation_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report += f"\nReport created on: {creation_timestamp}\n"

    return report

def generate_final_report(data, errors, start_date, end_date, output_dir, working_dir):
    report = StringIO()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    date_range = f"{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}"
    report.write(f"# {date_range}_Final_Expense_Report - Generated on {timestamp}\n\n")

    product_description = load_product_description(working_dir)
    report.write("## Product Description\n\n")
    report.write(product_description)
    report.write("\n\n")

    report.write("## Environment Information\n\n")
    report.write(f"Python Version: {sys.version}\n\n")

    config = load_config(working_dir)
    notes = load_notes(working_dir)

    report.write("## Processing Date Range\n\n")
    report.write(
        f"Transactions processed for date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}\n\n")

    report.write("## Status\n\n")
    if errors:
        report.write("### Known Bugs or Failures in this Cycle\n\n")
        for error in errors:
            report.write(f"- {error}\n")
    else:
        report.write("No known bugs or failures in this cycle.\n")
    report.write("\n")

    report.write("## Acceptance Test Results\n\n")
    if 'acceptance_test_results' in data and data['acceptance_test_results']:
        for test_name, result in data['acceptance_test_results'].items():
            status = 'Passed' if result else 'Failed'
            report.write(f"- {test_name}: {status}\n")
    else:
        report.write("No acceptance test results available.\n")
    report.write("\n")

    merged_df = data.get('merged_df')
    if merged_df is not None and not merged_df.empty:
        for employer in config.get('employers', []):
            employer_report = generate_employer_expense_report(merged_df, employer, config, notes, start_date, end_date)
            employer_report_path = os.path.join(output_dir,
                                                f"{date_range}_{employer.replace(' ', '_')}_expense_report.md")
            with open(employer_report_path, 'w') as f:
                f.write(employer_report)
            report.write(f"Expense report for {employer} saved to: {employer_report_path}\n")
            if PDF_GENERATION_AVAILABLE:
                try:
                    pdf_path = employer_report_path.replace('.md', '.pdf')
                    convert_markdown_to_pdf(employer_report_path, pdf_path)
                    report.write(f"PDF report for {employer} saved to: {pdf_path}\n")
                except Exception as e:
                    report.write(f"Failed to generate PDF for {employer}. Error: {str(e)}\n")
        report.write("\n")
    else:
        report.write("No transactions available for generating expense reports.\n\n")

    report.write("## Processed Files Summary\n\n")
    for file, columns in data.get('input_files', {}).items():
        report.write(f"- {file}: {', '.join(columns)}\n")
    report.write("\n")

    # Add timestamp of creation to the final report
    creation_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report.write(f"\nFinal report created on: {creation_timestamp}\n")

    return report.getvalue()

def load_config(working_dir):
    config_path = os.path.join(working_dir, 'config.json')
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Config file not found: {config_path}")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON in {config_path}: {str(e)}")
        return {}

def save_final_report(data, errors, start_date, end_date, output_dir, working_dir):
    report_content = generate_final_report(data, errors, start_date, end_date, output_dir, working_dir)
    date_range = f"{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}"
    report_file_name = f"{date_range}_Final_Expense_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    report_md_path = os.path.join(output_dir, f"{report_file_name}.md")
    report_pdf_path = None

    with open(report_md_path, 'w') as f:
        f.write(report_content)

    if PDF_GENERATION_AVAILABLE:
        try:
            report_pdf_path = os.path.join(output_dir, f"{report_file_name}.pdf")
            convert_markdown_to_pdf(report_md_path, report_pdf_path)
            logger.info(f"PDF report generated: {report_pdf_path}")
        except Exception as e:
            logger.warning(f"PDF generation failed. Error: {str(e)}")
            logger.info("The report will be available in Markdown format only.")
            report_pdf_path = None
    else:
        logger.info("PDF generation is not available. The report is available in Markdown format only.")

    return report_md_path, report_pdf_path, report_content

if __name__ == "__main__":
    logger.info("This script is not meant to be run directly. Please run main.py instead.")