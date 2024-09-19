# generate_expense_reports.py

import os
import pandas as pd
from datetime import datetime

def generate_expense_reports(config, merged_df, start_date, end_date, logger):
    output_dir = config['output_dir']
    employers = config['employers']

    final_report = f"# Expense Report\n\n"
    final_report += f"Period: {start_date.date()} to {end_date.date()}\n\n"

    if merged_df.empty:
        final_report += "No transactions found for the specified date range.\n\n"
        logger.warning("No transactions found in the merged DataFrame.")
        return final_report

    if 'employer' not in merged_df.columns:
        final_report += "Error: 'employer' column not found in merged DataFrame.\n\n"
        logger.error("'employer' column not found in merged DataFrame.")
        return final_report

    transactions_found = False
    for employer in employers:
        employer_df = merged_df[merged_df['employer'] == employer]

        if employer_df.empty:
            logger.info(f"No transactions found for {employer}")
            continue

        transactions_found = True
        report = f"## {employer} Expenses\n\n"
        report += "| Date | Description | Amount | Category | Note |\n"
        report += "|------|-------------|--------|----------|------|\n"

        for _, row in employer_df.iterrows():
            date = row.get('transaction_date', row.get('date', 'N/A'))
            description = row.get('description', 'N/A')
            amount = row.get('amount', row.get('debit', row.get('credit', 'N/A')))
            category = row.get('category', 'N/A')
            note = row.get('note', '')

            if isinstance(amount, (int, float)):
                amount_str = f"{amount:.2f}"
            else:
                amount_str = str(amount)

            report += f"| {date} | {description} | {amount_str} | {category} | {note} |\n"

        total = employer_df['amount'].sum() if 'amount' in employer_df.columns else 0
        report += f"\nTotal: ${total:.2f}\n\n"

        employer_report_file = os.path.join(output_dir, f"{employer.replace(' ', '_')}_expense_report.md")
        with open(employer_report_file, 'w') as f:
            f.write(report)
        logger.info(f"Expense report for {employer} saved to {employer_report_file}")

        final_report += report

    if not transactions_found:
        final_report += "No transactions found for any employer.\n\n"
        logger.warning("No transactions found for any employer.")

    logger.info("Expense reports generated")
    return final_report