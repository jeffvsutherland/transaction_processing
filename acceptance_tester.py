import pandas as pd
from typing import Dict, List
import logging
import re
#acceptance_tester.py
class AcceptanceTester:
    def __init__(self, input_dir: str, output_dir: str):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.logger = logging.getLogger(__name__)

    def run_tests(self, merged_df: pd.DataFrame, input_files: Dict[str, List[str]]) -> Dict:
        if merged_df.empty:
            self.logger.warning("Merged DataFrame is empty. Skipping acceptance tests.")
            return {"All tests": "Skipped - Empty DataFrame"}

        test_results = {
            "All required columns present": self.check_required_columns(merged_df),
            "No duplicate transactions": self.check_no_duplicates(merged_df),
            "All amounts are negative": self.check_negative_amounts(merged_df),
            "Date range is consistent": self.check_date_range(merged_df),
            "All transactions have a category": self.check_categories(merged_df),
            "All transactions have an employer": self.check_employers(merged_df),
            "All transactions have a valid currency": self.check_currency(merged_df),
            "All card columns have last four digits": self.check_card_digits(merged_df)
        }
        self.logger.info(f"Acceptance test results: {test_results}")
        return test_results

    def check_required_columns(self, df: pd.DataFrame) -> bool:
        required_columns = ['date', 'amount', 'vendor', 'Normalized Date']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            self.logger.warning(f"Missing columns: {missing_columns}")
            return False
        self.logger.info("All required columns are present")
        return True

    def check_no_duplicates(self, df: pd.DataFrame) -> bool:
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            self.logger.warning(f"Found {duplicates} duplicate transactions")
            return False
        self.logger.info("No duplicate transactions found")
        return True

    def check_negative_amounts(self, df: pd.DataFrame) -> bool:
        if 'amount' not in df.columns:
            self.logger.warning("'amount' column not found in DataFrame")
            return False
        positive_amounts = (df['amount'] > 0).sum()
        if positive_amounts > 0:
            self.logger.warning(f"Found {positive_amounts} transactions with positive amounts")
            return False
        self.logger.info("All amounts are negative (expenses)")
        return True

    def check_date_range(self, df: pd.DataFrame) -> bool:
        if 'Normalized Date' not in df.columns:
            self.logger.warning("'Normalized Date' column not found in DataFrame")
            return False
        date_range = df['Normalized Date'].max() - df['Normalized Date'].min()
        if date_range.days > 366:  # Allow for leap years
            self.logger.warning(f"Date range exceeds one year: {date_range.days} days")
            return False
        self.logger.info(f"Date range is consistent: {date_range.days} days")
        return True

    def check_categories(self, df: pd.DataFrame) -> bool:
        if 'category' not in df.columns:
            self.logger.warning("'category' column not found in DataFrame")
            return False
        missing_categories = df['category'].isna().sum()
        if missing_categories > 0:
            self.logger.warning(f"Found {missing_categories} transactions without categories")
            return False
        self.logger.info("All transactions have categories")
        return True

    def check_employers(self, df: pd.DataFrame) -> bool:
        if 'employer' not in df.columns:
            self.logger.warning("'employer' column not found in DataFrame")
            return False
        missing_employers = df['employer'].isna().sum()
        if missing_employers > 0:
            self.logger.warning(f"Found {missing_employers} transactions without employers")
            return False
        self.logger.info("All transactions have employers")
        return True

    def check_currency(self, df: pd.DataFrame) -> bool:
        if 'currency' not in df.columns:
            self.logger.warning("'currency' column not found in DataFrame")
            return False
        invalid_currencies = df[~df['currency'].isin(['USD', 'EUR', 'GBP', 'JPY', 'CAD'])].shape[0]
        if invalid_currencies > 0:
            self.logger.warning(f"Found {invalid_currencies} transactions with invalid currencies")
            return False
        self.logger.info("All transactions have valid currencies")
        return True

    def check_card_digits(self, df: pd.DataFrame) -> bool:
        if 'Card' not in df.columns:
            self.logger.warning("'Card' column not found in DataFrame")
            return False
        invalid_cards = df[~df['Card'].apply(lambda x: bool(re.match(r'^\d{4}$', str(x))))].shape[0]
        if invalid_cards > 0:
            self.logger.warning(f"Found {invalid_cards} transactions with invalid card numbers")
            return False
        self.logger.info("All card columns have last four digits")
        return True