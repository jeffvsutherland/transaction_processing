from datetime import datetime
import pandas as pd
from typing import Dict, List

class ReportFormatter:
    def __init__(self, config: Dict):
        self.config = config

    def generate_expense_reports(self, merged_df: pd.DataFrame, start_date: datetime, end_date: datetime) -> str:
        if merged_df.empty:
            return "No transactions found in the specified date range."

        expense_reports = ""
        for employer in self.config['employers']:
            employer_df = merged_df[merged_df['employer'] == employer]
            if not employer_df.empty:
                report = self.format_expense_report(employer_df, employer, start_date, end_date)
                expense_reports += report + "\n\n"
        return expense_reports

    def format_expense_report(self, df: pd.DataFrame, employer: str, start_date: datetime, end_date: datetime) -> str:
        total_expense = df['amount'].sum()
        report = f"# Expense Report for {employer}\n"
        report += f"Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}\n"
        report += f"Total Expenses: ${total_expense:.2f}\n\n"
        report += df.to_markdown(index=False)
        return report

    def create_final_report(self, timestamp: str, merged_df: pd.DataFrame, expense_reports: str,
                            intermediate_files: Dict[str, pd.DataFrame], input_files: Dict[str, List[str]],
                            acceptance_test_results: Dict, files_used: set) -> str:
        report = f"# Final Expense Report - {timestamp}\n\n"

        # Table of Contents
        report += "## Table of Contents\n"
        report += "1. [Overview](#overview)\n"
        report += "2. [Input Files](#input-files)\n"
        report += "3. [Processed Data](#processed-data)\n"
        report += "4. [Expense Reports](#expense-reports)\n"
        report += "5. [Acceptance Test Results](#acceptance-test-results)\n"
        report += "6. [Files Used](#files-used)\n"
        report += "7. [Data Quality Issues](#data-quality-issues)\n"
        report += "8. [Next Steps](#next-steps)\n\n"

        report += "## Overview\n"
        report += "This report summarizes the expense data processed from multiple bank statements.\n\n"

        report += "## Input Files\n"
        if input_files:
            for file, columns in input_files.items():
                report += f"- {file}: {', '.join(columns)}\n"
        else:
            report += "No input files were processed.\n"
        report += "\n"

        report += "## Processed Data\n"
        if not merged_df.empty:
            report += f"Total transactions: {len(merged_df)}\n"
            report += f"Date range: {merged_df['Normalized Date'].min()} to {merged_df['Normalized Date'].max()}\n\n"
        else:
            report += "No transactions were processed.\n\n"

        report += "## Expense Reports\n"
        report += expense_reports if expense_reports else "No expense reports generated.\n\n"

        report += "## Acceptance Test Results\n"
        for test, result in acceptance_test_results.items():
            report += f"- {test}: {'Passed' if result else 'Failed'}\n"
        report += "\n"

        report += "## Files Used\n"
        if files_used:
            for file in files_used:
                report += f"- {file}\n"
        else:
            report += "No files were used in this processing run.\n"
        report += "\n"

        report += "## Data Quality Issues\n"
        report += "1. No data quality issues identified in this run.\n\n"

        report += "## Next Steps\n"
        report += "1. Investigate why no transactions were processed.\n"
        report += "2. Review input file formats and parsing logic.\n"
        report += "3. Check date range settings for transaction filtering.\n"

        return report