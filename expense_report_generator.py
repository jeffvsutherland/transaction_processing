# expense_report_generator.py

import os
import pandas as pd
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ExpenseReportGenerator:
    def __init__(self, config, notes):
        self.config = config
        self.notes = notes

    def generate_report(self, df, employer, start_date, end_date):
        logger.info(f"Generating expense report for {employer}")

        # Filter data for the specific employer and date range
        mask = (df['employer'] == employer) & (df['date'] >= start_date) & (df['date'] <= end_date)
        employer_df = df[mask].copy()

        if employer_df.empty:
            logger.warning(f"No transactions found for {employer} in the specified date range")
            return f"No transactions found for {employer} in the specified date range."

        # Sort the dataframe
        employer_df = employer_df.sort_values(['category', 'date'])

        # Generate the report
        report = self._generate_report_content(employer_df, employer, start_date, end_date)

        logger.info(f"Expense report generated for {employer}")
        return report

    def _generate_report_content(self, df, employer, start_date, end_date):
        report = f"# Expense Report for {employer}\n\n"
        report += f"Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}\n\n"

        # Group by category
        grouped = df.groupby('category')
        total_amount = 0

        for category, group in grouped:
            report += f"## {category}\n\n"

            # Generate table
            table = group[['date', 'description', 'amount']].to_markdown(index=False)
            report += table + "\n\n"

            category_total = group['amount'].sum()
            report += f"Category Total: ${category_total:.2f}\n\n"
            total_amount += category_total

        report += f"## Total Amount: ${total_amount:.2f}\n\n"

        # Add notes
        report += "## Notes\n\n"
        for note in self.notes.get('notes', []):
            report += f"- {note}\n"

        # Add timestamp
        report += f"\nReport generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"

        return report

    def save_report(self, report, employer, output_dir):
        # Create a valid filename
        filename = f"{employer.replace(' ', '_')}_expense_report.md"
        filepath = os.path.join(output_dir, filename)

        with open(filepath, 'w') as f:
            f.write(report)

        logger.info(f"Expense report for {employer} saved to {filepath}")
        return filepath


if __name__ == "__main__":
    # This allows for easy testing of this module independently
    import json
    from data_processor import DataProcessor

    with open('config.json', 'r') as f:
        config = json.load(f)

    with open('note.json', 'r') as f:
        notes = json.load(f)

    # Process some data
    data_processor = DataProcessor(config)
    df = data_processor.process()

    # Generate a report
    generator = ExpenseReportGenerator(config, notes)
    start_date = datetime.strptime(config['date_range']['start_date'], '%Y-%m-%d')
    end_date = datetime.strptime(config['date_range']['end_date'], '%Y-%m-%d')

    for employer in config['employers']:
        report = generator.generate_report(df, employer, start_date, end_date)
        generator.save_report(report, employer, config['output_dir'])

    print("Test run completed. Check the output directory for generated reports.")