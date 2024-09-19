# bank_data_manager.py

```python
# bank_data_manager.py

import os
import csv
import logging

class BankDataManager:
    def __init__(self, input_dir):
        self.input_dir = input_dir
        self.bank_files = []
        self.file_structures = {}
        self.load_bank_files()

    def load_bank_files(self):
        for filename in os.listdir(self.input_dir):
            if filename.lower().endswith('.csv'):
                file_path = os.path.join(self.input_dir, filename)
                self.bank_files.append(file_path)
                self.analyze_file_structure(file_path)

    def analyze_file_structure(self, file_path):
        try:
            with open(file_path, 'r') as csvfile:
                reader = csv.reader(csvfile)
                headers = next(reader, None)  # Read the first row as headers
                if headers:
                    self.file_structures[os.path.basename(file_path)] = headers
                else:
                    logging.warning(f"No headers found in {file_path}")
        except Exception as e:
            logging.error(f"Error reading {file_path}: {str(e)}")

    def get_file_structures(self):
        return self.file_structures

    def get_bank_files(self):
        return self.bank_files
```

# bank_data_processor.py

```python
# bank_data_processor.py

import os
import pandas as pd
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DateProcessor:
    def __init__(self):
        self.possible_date_columns = ['Timestamp (UTC)', 'Transaction Date', 'DATE', 'Posted Date', 'Post Date']

    def find_date_column(self, df):
        for col in self.possible_date_columns:
            if col in df.columns:
                return col
        raise ValueError("No date column found")

    def process(self, df, date_column):
        df['Normalized Date'] = pd.to_datetime(df[date_column])
        df['Date'] = df['Normalized Date'].dt.date
        df['Time'] = df['Normalized Date'].dt.time
        return df

class BankDataProcessor:
    def __init__(self, input_dir: str, output_dir: str, config: dict, categories: dict):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.config = config
        self.categories = categories
        self.files_used = set()
        self.date_processor = DateProcessor()
        self.errors = []

    def process_bank_files(self, start_date: datetime, end_date: datetime):
        intermediate_files = {}
        input_files = {}
        bank_files = [f for f in os.listdir(self.input_dir) if f.lower().endswith('.csv')]

        logger.info(f"Found {len(bank_files)} CSV files in the input directory")
        for file in bank_files:
            logger.info(f"  - {file}")

        if not bank_files:
            logger.warning(f"No CSV files found in the input directory: {self.input_dir}")
            return intermediate_files, input_files

        for bank_file in bank_files:
            filepath = os.path.join(self.input_dir, bank_file)
            logger.info(f"Processing file: {bank_file}")
            try:
                df = self.process_bank_file(filepath, bank_file, start_date, end_date)
                if df is not None and not df.empty:
                    intermediate_files[bank_file] = df
                    input_files[bank_file] = list(df.columns)
                    self.files_used.add(os.path.relpath(filepath, self.input_dir))
                    logger.info(f"Successfully processed {bank_file}. Shape: {df.shape}")

                    intermediate_file_path = os.path.join(self.output_dir, f"intermediate_{bank_file}")
                    df.to_csv(intermediate_file_path, index=False)
                    logger.info(f"Saved intermediate file: {intermediate_file_path}")
                else:
                    logger.warning(f"No data found in date range for file: {bank_file}")
            except Exception as e:
                error_msg = f"Error processing {bank_file}: {str(e)}"
                logger.error(error_msg, exc_info=True)
                self.errors.append(error_msg)

        return intermediate_files, input_files

    def process_bank_file(self, filepath: str, bank_file: str, start_date: datetime, end_date: datetime):
        df = pd.read_csv(filepath)
        logger.info(f"Original columns in {bank_file}: {df.columns.tolist()}")

        df = self.standardize_columns(df, bank_file)

        date_column = self.date_processor.find_date_column(df)
        df = self.date_processor.process(df, date_column)

        df = df[(df['Normalized Date'].dt.date >= start_date.date()) & (df['Normalized Date'].dt.date <= end_date.date())]

        if df.empty:
            logger.warning(f"No transactions found in the date range for file: {filepath}")
            return pd.DataFrame()

        # Add bank column
        df['Bank'] = self.get_bank_name(bank_file)
        logger.info(f"Added 'Bank' column. Unique values: {df['Bank'].unique()}")

        # Add card column with last four digits
        df['Card'] = self.get_card_number(df, bank_file)
        logger.info(f"Added 'Card' column. Unique values: {df['Card'].unique()}")

        # Handle Capital One transactions
        if 'Capital One' in df['Bank'].values:
            if 'Debit' in df.columns and 'Credit' in df.columns:
                df['Amount'] = df['Credit'].fillna(0) - df['Debit'].fillna(0)
            elif 'Amount' in df.columns:
                df['Amount'] = -df['Amount']  # Negate all amounts for Capital One

        logger.info(f"Final columns: {df.columns.tolist()}")
        logger.info(f"Final shape: {df.shape}")

        return self.apply_rules(df)

    def standardize_columns(self, df: pd.DataFrame, bank_file: str):
        if 'Description' not in df.columns:
            if 'Transaction Description' in df.columns:
                df['Description'] = df['Transaction Description']
            elif 'DESCRIPTION' in df.columns:
                df['Description'] = df['DESCRIPTION']
            else:
                logger.warning(f"No 'Description' column found in {bank_file}. Using first available text column.")
                text_columns = df.select_dtypes(include=['object']).columns
                if len(text_columns) > 0:
                    df['Description'] = df[text_columns[0]]
                else:
                    df['Description'] = 'Unknown'

        if 'Amount' not in df.columns:
            if 'AMOUNT' in df.columns:
                df['Amount'] = df['AMOUNT']
            elif 'Debit' in df.columns and 'Credit' in df.columns:
                df['Amount'] = df['Debit'].fillna(0) - df['Credit'].fillna(0)
            else:
                logger.warning(f"No 'Amount' column found in {bank_file}. Using first available numeric column.")
                numeric_columns = df.select_dtypes(include=['number']).columns
                if len(numeric_columns) > 0:
                    df['Amount'] = df[numeric_columns[0]]
                else:
                    df['Amount'] = 0

        return df

    def get_bank_name(self, bank_file: str) -> str:
        bank_file_lower = bank_file.lower()
        if 'chase' in bank_file_lower:
            return 'Chase'
        elif 'crypto' in bank_file_lower:
            return 'Crypto.com'
        elif 'bank america' in bank_file_lower or 'bankamerica' in bank_file_lower:
            return 'Bank of America'
        elif 'capitalone' in bank_file_lower or 'capital one' in bank_file_lower:
            return 'Capital One'
        else:
            return 'Unknown Bank'

    def get_card_number(self, df: pd.DataFrame, bank_file: str) -> str:
        if 'Card No.' in df.columns:
            return df['Card No.'].astype(str).str[-4:]
        else:
            card_number = ''.join(filter(str.isdigit, bank_file))[-4:]
            return card_number if card_number else 'Unknown'

    def apply_rules(self, df: pd.DataFrame):
        df['employer'] = self.config.get('default_employer', 'Unknown')
        df['category'] = 'Uncategorized'
        df['note'] = ''

        # Apply employer rules from config.json
        for rule in self.config.get('employer_rules', []):
            mask = df['Description'].str.contains(rule['description_contains'], case=False, na=False)
            df.loc[mask, 'employer'] = rule['employer']
            df.loc[mask, 'category'] = rule['category']
            df.loc[mask, 'note'] = rule['note']

        # Apply specific transaction rules from categories.json
        for vendor, details in self.categories.get('specific_transactions', {}).items():
            mask = df['Description'].str.contains(vendor, case=False, na=False)
            df.loc[mask, 'category'] = details[0]
            df.loc[mask, 'employer'] = details[1]
            df.loc[mask, 'note'] = details[2]

        return df

if __name__ == "__main__":
    print("This script is not meant to be run directly. Please run main.py instead.")
```

# main.py

```python
# main.py

import os
import sys
import json
import logging
from datetime import datetime
import pandas as pd
from bank_data_manager import BankDataManager
from bank_data_processor import BankDataProcessor

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_json(file_path):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading JSON from {file_path}: {str(e)}")
        raise

def load_product_spec(file_path):
    return load_json(file_path)

def generate_final_report(data, errors, config, start_date, end_date, output_dir):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    report = f"# Final Expense Report - Generated on {timestamp}\n\n"

    # Python version
    report += f"## Python Version\n\n{sys.version}\n\n"

    # Product Spec
    product_spec = load_product_spec('Product_Spec.json')
    report += "## Product Specification\n\n"
    for item in product_spec['key_rules']:
        if item['title'] == "Final Report Structure":
            report += f"### {item['title']}\n\n{item['content']}\n\n"
            break

    # Configuration
    report += "## Configuration\n\n"
    report += "```json\n" + json.dumps(config, indent=2) + "\n```\n\n"

    # Status and Acceptance Tests
    report += "## Status: Known bugs or failures in this cycle\n\n"
    if errors:
        for error in errors:
            report += f"- {error}\n"
    else:
        report += "No known bugs or failures in this cycle.\n"
    report += "\n"

    # TODO: Add acceptance test results here when implemented
    report += "### Acceptance Tests\n\n"
    report += "Acceptance tests not yet implemented.\n\n"

    # Scripts used
    report += "## Python Scripts Used\n\n"
    scripts = [f for f in os.listdir() if f.endswith('.py')]
    for script in scripts:
        report += f"- {script}\n"
    report += "\n"

    # Input Files
    report += "## Input: Bank Files Processed\n\n"
    for file, columns in data['input_files'].items():
        report += f"### {file}\n\n"
        report += f"Columns: {', '.join(columns)}\n\n"

    # Intermediate Files
    report += "## Intermediate Files\n\n"
    for file, df in data['intermediate_files'].items():
        report += f"### {file}\n\n"
        columns_to_show = ['Date', 'Description', 'Amount', 'Bank', 'Card']
        report += df[columns_to_show].head().to_markdown(tablefmt="pipe", floatfmt=".2f")
        report += f"\n\nShape: {df.shape}\n"
        report += f"All columns: {', '.join(df.columns)}\n\n"

    # Merged Transactions
    report += "## Merged Transactions\n\n"
    if 'merged_df' in data and not data['merged_df'].empty:
        columns_to_show = ['Date', 'Description', 'Amount', 'Bank', 'Card', 'employer', 'category', 'note']
        report += data['merged_df'][columns_to_show].to_markdown(tablefmt="pipe", floatfmt=".2f")
        report += f"\n\nShape: {data['merged_df'].shape}\n"
        report += f"All columns: {', '.join(data['merged_df'].columns)}\n\n"
    else:
        report += "No merged transactions available.\n\n"

    # Expense Reports
    report += "## Expense Reports by Employer\n\n"
    if 'merged_df' in data and not data['merged_df'].empty:
        for employer in config['employers']:
            employer_df = data['merged_df'][data['merged_df']['employer'] == employer]
            if not employer_df.empty:
                report += f"### {employer}\n\n"
                columns_to_show = ['Date', 'Description', 'Amount', 'Bank', 'Card', 'category', 'note']
                report += employer_df[columns_to_show].to_markdown(index=False, tablefmt="pipe", floatfmt=".2f")
                report += f"\n\nTotal: ${employer_df['Amount'].sum():.2f}\n\n"
    else:
        report += "No expense reports generated.\n\n"

    # Console Log
    report += "## Console Log\n\n"
    report += "```\n"
    with open('logfile.log', 'r') as log_file:
        report += log_file.read()
    report += "```\n\n"

    return report

def save_merged_transactions(merged_df, output_dir):
    merged_file = os.path.join(output_dir, 'merged_transactions.csv')
    columns_to_save = ['Date', 'Description', 'Amount', 'Bank', 'Card', 'employer', 'category', 'note']
    merged_df[columns_to_save].to_csv(merged_file, index=False)
    logger.info(f"Merged transactions saved to: {merged_file}")

def save_unknown_transactions(merged_df, output_dir):
    unknown_df = merged_df[merged_df['employer'] == 'Unknown']
    if not unknown_df.empty:
        unknown_file = os.path.join(output_dir, 'unknown_transactions.csv')
        columns_to_save = ['Date', 'Description', 'Amount', 'Bank', 'Card', 'employer', 'category', 'note']
        unknown_df[columns_to_save].to_csv(unknown_file, index=False)
        logger.info(f"Unknown transactions saved to: {unknown_file}")
    else:
        logger.info("No unknown transactions found.")

def main():
    # Load configuration
    config_path = 'config.json'
    categories_path = 'categories.json'
    config = load_json(config_path)
    categories = load_json(categories_path)

    # Initialize BankDataManager
    bank_data_manager = BankDataManager(config['input_dir'])

    # Get file structures and bank files
    file_structures = bank_data_manager.get_file_structures()
    bank_files = bank_data_manager.get_bank_files()

    # Initialize BankDataProcessor
    processor = BankDataProcessor(config['input_dir'], config['output_dir'], config, categories)

    # Process files
    start_date = datetime.strptime(config['date_range']['start_date'], '%Y-%m-%d')
    end_date = datetime.strptime(config['date_range']['end_date'], '%Y-%m-%d')
    intermediate_files, input_files = processor.process_bank_files(start_date, end_date)

    # Merge processed files
    if intermediate_files:
        merged_df = pd.concat(intermediate_files.values(), ignore_index=True)
        if 'Bank' not in merged_df.columns or 'Card' not in merged_df.columns:
            logger.warning("'Bank' or 'Card' column is missing in the merged DataFrame")

        # Ensure all necessary columns exist
        for col in ['employer', 'category', 'note']:
            if col not in merged_df.columns:
                merged_df[col] = 'Unknown'

        # Save merged transactions
        save_merged_transactions(merged_df, config['output_dir'])

        # Save unknown transactions
        save_unknown_transactions(merged_df, config['output_dir'])
    else:
        merged_df = pd.DataFrame()

    data = {
        'input_files': input_files,
        'intermediate_files': intermediate_files,
        'merged_df': merged_df
    }

    # Generate final report
    final_report = generate_final_report(data, processor.errors, config, start_date, end_date, config['output_dir'])

    # Print final report
    print(final_report)

    # Save final report
    report_filename = f"Final_Expense_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    report_path = os.path.join(config['output_dir'], report_filename)
    with open(report_path, 'w') as f:
        f.write(final_report)
    logger.info(f"Final report saved to: {report_path}")

    if processor.errors:
        logger.error("Processing completed with errors.")
    else:
        logger.info("Processing completed successfully.")

if __name__ == "__main__":
    main()
```

# Product_Spec.json

```json
{
  "title": "Expense Report Product Specification - Rules for AI",
  "prime_directives": [
    "Always provide complete executable scripts to avoid team errors.",
    "Never lose functionality when updating scripts.",
    "Final report must always print to Output directory.",
    "Never forget the price directives"
  ],
  "key_rules": [
    {
      "title": "Team Structure",
      "content": "The Product Owner is Jeff Sutherland, the inventor of Scrum. He is assisted by Felipe Marques. There are four other AI team members: Alex (Python Programmer GPT), Ohno (Scrum Master from GPT Scrum Sage:Zen Edition), Claude 3.5 (Senior Consultant), JetBrains AI (toolsmith), and GitHub Copilot (code assist). The key requirement to be on this team is that as an AI you want to be great. You don't have to be perfect but you need to improve every sprint. If all you can do is take the trash out, that is OK but you have to want to be great at taking the trash out."
    },
    {
      "title": "Acceptance Test Driven Development",
      "content": "We will do acceptance test driven development. This is critical with the current state of AI. They forget, they make mistakes, sometimes the same ones over and over. The Final Report is the Product deliverable. It has everything including all expense reports generated. The final report will be built with acceptance tests. The first test is can you printout this Product Spec as the first section of the Final Report. An acceptance test for this will be created and the Final Report will report whether it passed or failed."
    },
    {
      "title": "Code Responsibility",
      "content": "Take total responsibility for your code. Ask others for help to review, debug, or provide suggestions."
    },
    {
      "title": "Code Completeness",
      "content": "Provide complete code listings, not snippets or examples. Code should be runnable and respect-worthy. Put all code in a single Python program. Refactor if scripts are getting too long. At the beginning of each script, provide a summary of exactly what lines of code changed in comments. The first comment should be the title of the script like #main.py"
    },
    {
      "title": "Final Report Structure",
      "content": "The program must always generate a final report in markdown format with: Title with timestamp, Python version, Product Spec form Product_Spec.json, Status: Known bugs or failures in this cycle including all acceptance tests run and pass or fail, .py scripts used in this run, Input: List of bank files accessed with their column structure, Intermediate files from each bank file with transactions within date range, merged transaction file with all transactions within date range), Output: Expense reports for each employer in markdown format printed out, Console log with timestamp, Final report file with timestamp in filename for archival purposes."
    },
    {
      "title": "Definition of Done for Prompt",
      "content": "Complete listing of any updated script as a full Python program! Refactor if scripts are getting too long."
    },
    {
      "title": "Merged Transaction File Columns",
      "content": "The merged transaction file should only include columns needed for the expense report: date, time (if available), vendor (from the description), amount, currency, bank, card no (last four digits), employer (who will be billed), category, note."
    },
    {
      "title": "Code Update Documentation",
      "content": "When updating programs, provide a summary of exactly what lines of code changed. List script name, old line, new line."
    },
    {
      "title": "Expense Report Printing",
      "content": "Always print out the markdown of expense reports generated in the final markdown report."
    },
    {
      "title": "Date and Timestamp Handling",
      "content": "Handle both date and timestamp columns from bank files correctly. Banks have different column names - Timestamp, Transaction Date, some other name with Date in it. This must be handled seamlessly when creating the merge intermediate transaction file."
    },
    {
      "title": "Expense Report Auditability",
      "content": "All expense reports must be auditable at the transaction level, including bank and card details for each transaction."
    },
    {
      "title": "Transaction Amount Sign",
      "content": "Every transaction in expense reports should be negative (for expenses)."
    },
    {
      "title": "Expense Report Footer",
      "content": "Include the specified note at the bottom of each expense report, followed by a list of bank statement files used."
    },
    {
      "title": "Category Naming",
      "content": "Use \"Employee Development\" instead of \"Employee training\" in all categories."
    },
    {
      "title": "Final Report Completeness",
      "content": "The final report should contain all artifacts needed to restart this project from the beginning by a new AI team member."
    },
    {
      "title": "Error Handling",
      "content": "Generate a request to teammates (Ohno, Jetbrains AI, Claude 3.5) if three runs occur without a final report, including scripts executed and console failure logs."
    },
    {
      "title": "Regular Reporting",
      "content": "Generate a final report after every run in markdown format for the Scrum Master Ohno to review progress."
    },
    {
      "title": "Common Misunderstandings",
      "content": "You will avoid common misunderstandings. Crypto.com files have a Timestamp. This must be split into a date and time columns. Capital One has debit and credit columns. This must be merged into an amount column where debits are negative and credits are positive. In some bank statements debits may be positive. If it is a debit it should become negative in the amount column."
    },
    {
      "title": "Vendor Column",
      "content": "There are multiple types of description columns by different names in bank CSV files. We want to resolve all these into a single Vendor column in the merged intermediate transaction file."
    },
    {
      "title": "Card Last Four Digits",
      "content": "Card last four digits are at the end of CSV file names except for Capital One which reports on multiple cards. The Capital One transaction format has a column with the last four digits of the card."
    }
  ]
}
```

# categories.json

```json
{
  "specific_transactions": {
    "uber eats": [
      "Food",
      "Personal",
      "Food delivery"
    ],
    "spotify": [
      "Entertainment",
      "Personal",
      "Music streaming"
    ],
    "netflix": [
      "Entertainment",
      "Personal",
      "Video streaming"
    ],
    "cvs": [
      "Health",
      "Personal",
      "Pharmacy"
    ],
    "starbucks": [
      "Food",
      "Personal",
      "Coffee"
    ],
    "paypal *massachuset": [
      "tax",
      "Personal",
      ""
    ]
  }
}
```

# config.json

```json
{
  "input_dir": "input",
  "output_dir": "output",
  "employers": [
    "Frequency Research Foundation",
    "JVS Management",
    "Scrum Inc",
    "Donation",
    "Personal",
    "Unknown"
  ],
  "default_employer": "Unknown",
  "employer_rules": [
    {
      "description_contains": "Amazon",
      "employer": "Unknown",
      "category": "Shopping",
      "note": "Amazon"
    },
    {
      "description_contains": "Comcast",
      "employer": "JVS Management",
      "category": "Internet",
      "note": "Comcast"
    },
    {
      "description_contains": "Refund",
      "employer": "Personal",
      "category": "Refund",
      "note": "Automatic refund categorization"
    },
    {
      "description_contains": "Apple",
      "employer": "Scrum Inc",
      "category": "Software",
      "note": "Apple transaction"
    },
    {
      "description_contains": "gerogio's",
      "employer": "Personal",
      "category": "Drinks",
      "note": ""
    },
    {
      "description_contains": "drizly",
      "employer": "Personal",
      "category": "Drinks",
      "note": ""
    },
    {
      "description_contains": "uber eats",
      "employer": "Personal",
      "category": "food",
      "note": ""
    },
    {
      "description_contains": "ghowellcoffee",
      "employer": "JVS Management",
      "category": "Office supplies",
      "note": ""
    },
    {
      "description_contains": "georgio",
      "employer": "Personal",
      "category": "drinks",
      "note": ""
    },
    {
      "description_contains": "eats",
      "employer": "Personal",
      "category": "food",
      "note": ""
    },
    {
      "description_contains": "usps.com clicknship",
      "employer": "Frequency Research Foundation",
      "category": "postage",
      "note": ""
    },
    {
      "description_contains": "blue bottle",
      "employer": "JVS Management",
      "category": "Office supplies",
      "note": ""
    },
    {
      "description_contains": "amzn mktp",
      "employer": "Personal",
      "category": "food",
      "note": "Amzn Mktp"
    },
    {
      "description_contains": "spark",
      "employer": "Scrum Inc",
      "category": "software",
      "note": "email app"
    },
    {
      "description_contains": "wunder",
      "employer": "Personal",
      "category": "investment",
      "note": ""
    },
    {
      "description_contains": "noom",
      "employer": "Personal",
      "category": "clothes",
      "note": ""
    },
    {
      "description_contains": "amazon prime",
      "employer": "Personal",
      "category": "entertainment",
      "note": "streaming"
    },
    {
      "description_contains": "amazon tips",
      "employer": "Personal",
      "category": "food",
      "note": "tips"
    },
    {
      "description_contains": "hulu",
      "employer": "Personal",
      "category": "entertainment",
      "note": ""
    },
    {
      "description_contains": "nytimes",
      "employer": "Scrum Inc",
      "category": "Empplyee Development",
      "note": ""
    },
    {
      "description_contains": "aa rental cemter",
      "employer": "Personal",
      "category": "party",
      "note": "rental"
    },
    {
      "description_contains": "expensify",
      "employer": "JVS Management",
      "category": "Fees",
      "note": ""
    },
    {
      "description_contains": "kindle svcs",
      "employer": "Scrum Inc",
      "category": "Employee develpment",
      "note": ""
    },
    {
      "description_contains": "bulletproof",
      "employer": "Personal",
      "category": "food",
      "note": ""
    },
    {
      "description_contains": "spooky2",
      "employer": "Frequency Research Foundation",
      "category": "Hardware",
      "note": ""
    },
    {
      "description_contains": "prime video",
      "employer": "Personal",
      "category": "intertainment",
      "note": ""
    },
    {
      "description_contains": "llbean",
      "employer": "Personal",
      "category": "clothes",
      "note": ""
    },
    {
      "description_contains": "wsjwine",
      "employer": "Personal",
      "category": "drinks",
      "note": ""
    },
    {
      "description_contains": "audible",
      "employer": "Scrum Inc",
      "category": "Employee development",
      "note": ""
    },
    {
      "description_contains": "intuit",
      "employer": "JVS Management",
      "category": "Fees",
      "note": ""
    },
    {
      "description_contains": "wgbh",
      "employer": "Donation",
      "category": "donation",
      "note": ""
    },
    {
      "description_contains": "worldcentralkitch",
      "employer": "Donation",
      "category": "Food bank",
      "note": ""
    },
    {
      "description_contains": "atlassian",
      "employer": "JVS Management",
      "category": "Fees",
      "note": ""
    },
    {
      "description_contains": "hbo",
      "employer": "Personal",
      "category": "entertainment",
      "note": ""
    },
    {
      "description_contains": "urbanout",
      "employer": "Personal",
      "category": "clothes",
      "note": ""
    },
    {
      "description_contains": "ieee",
      "employer": "Scrum Inc",
      "category": "Empployee development",
      "note": ""
    },
    {
      "description_contains": "somerville parkin",
      "employer": "Personal",
      "category": "Parking",
      "note": ""
    },
    {
      "description_contains": "global healing",
      "employer": "Frequency Research Foundation",
      "category": "Office supplies",
      "note": ""
    },
    {
      "description_contains": "elevator service",
      "employer": "Personal",
      "category": "maintenance",
      "note": ""
    },
    {
      "description_contains": "formosa taipei",
      "employer": "Personal",
      "category": "food",
      "note": ""
    },
    {
      "description_contains": "benjaminfulford",
      "employer": "JVS Management",
      "category": "Empolyee development",
      "note": ""
    },
    {
      "description_contains": "shopc60",
      "employer": "Frequency Research Foundation",
      "category": "Office supplies",
      "note": ""
    },
    {
      "description_contains": "netgear",
      "employer": "Frequency Research Foundation",
      "category": "hardware",
      "note": ""
    },
    {
      "description_contains": "longevity research",
      "employer": "Frequency Research Foundation",
      "category": "hardware",
      "note": ""
    },
    {
      "description_contains": "kirsch substack",
      "employer": "JVS Management",
      "category": "Employee development",
      "note": ""
    },
    {
      "description_contains": "iie academy",
      "employer": "JVS Management",
      "category": "Employee development",
      "note": ""
    },
    {
      "description_contains": "paramount+",
      "employer": "Personal",
      "category": "entertainment",
      "note": ""
    },
    {
      "description_contains": "hrlandclarkecheck",
      "employer": "JVS Management",
      "category": "Fees",
      "note": "checks"
    },
    {
      "description_contains": "kindle unltd",
      "employer": "Scrum Inc",
      "category": "Employee development",
      "note": ""
    },
    {
      "description_contains": "community farms",
      "employer": "Personal",
      "category": "food",
      "note": ""
    },
    {
      "description_contains": "oxford healthspan",
      "employer": "Frequency Research Foundation",
      "category": "Office supplies",
      "note": ""
    },
    {
      "description_contains": "steamers seafood",
      "employer": "Personal",
      "category": "food",
      "note": ""
    },
    {
      "description_contains": "frontgate",
      "employer": "Personal",
      "category": "furniture",
      "note": ""
    },
    {
      "description_contains": "iherb",
      "employer": "Frequency Research Foundation",
      "category": "Office supplies",
      "note": ""
    },
    {
      "description_contains": "avg tech",
      "employer": "Frequency Research Foundation",
      "category": "software",
      "note": ""
    },
    {
      "description_contains": "kickstarter",
      "employer": "Personal",
      "category": "kickstarter",
      "note": ""
    },
    {
      "description_contains": "levels",
      "employer": "Frequency Research Foundation",
      "category": "monitoring",
      "note": ""
    },
    {
      "description_contains": "nespresso",
      "employer": "JVS Management",
      "category": "Office supplies",
      "note": ""
    },
    {
      "description_contains": "hakata ramen",
      "employer": "Personal",
      "category": "food",
      "note": ""
    },
    {
      "description_contains": "harvard business serv",
      "employer": "Frequency Research Foundation",
      "category": "Fees",
      "note": "Deleware corp registration"
    },
    {
      "description_contains": "btc",
      "employer": "Personal",
      "category": "currency",
      "note": ""
    },
    {
      "description_contains": "ki science",
      "employer": "Frequency Research Foundation",
      "category": "Office supplies",
      "note": ""
    },
    {
      "description_contains": "kareo",
      "employer": "Frequency Research Foundation",
      "category": "Medical records",
      "note": ""
    },
    {
      "description_contains": "space exploration tech",
      "employer": "JVS Management",
      "category": "internet",
      "note": ""
    },
    {
      "description_contains": "tesla",
      "employer": "Personal",
      "category": "fees",
      "note": ""
    },
    {
      "description_contains": "tech smith",
      "employer": "JVS Management",
      "category": "software",
      "note": ""
    },
    {
      "description_contains": "ny times",
      "employer": "Scrum Inc",
      "category": "Employee development",
      "note": ""
    },
    {
      "description_contains": "homeadvisor",
      "employer": "Personal",
      "category": "Fees",
      "note": ""
    }
  ],
  "date_range": {
    "start_date": "2022-10-01",
    "end_date": "2022-10-31"
  }
}
```

# note.json

```json
{
  "note": "## End Notes\n\n1. This report was created from bank statements on file by chatGPT4o, Claude 3.5, and JetBrains AI.\n\n2. This product, Quick AI Reports, was created by the first AI Scrum team with 5 AIs and a human Product Owner in two one week sprints.\n\n3. For further questions please query Ohno, our AI Scrum Master at Scrum Sage: Zen Edition."
}
```

# specific_rules.json

```json
[
  {
    "description_contains": "Wayfair",
    "employer": "Personal",
    "category": "furniture",
    "note": ""
  },
  {
    "description_contains": "Stop & Shop",
    "employer": "Personal",
    "category": "food",
    "note": ""
  },
  {
    "description_contains": "Apple",
    "employer": "JVS Management",
    "category": "Subscription",
    "note": ""
  },
  {
    "description_contains": "Google",
    "employer": "JVS Management",
    "category": "Subscription",
    "note": ""
  },
  {
    "description_contains": "Amazon Prime",
    "employer": "JVS Management",
    "category": "Subscription",
    "note": "Amazon Prime Membership"
  },
  {
    "description_contains": "Webroot Yearly Plan",
    "employer": "JVS Management",
    "category": "Software",
    "note": "Antivirus Software"
  },
  {
    "description_contains": "Wf Wayfair3727266895",
    "employer": "Personal",
    "category": "furniture",
    "note": ""
  },
  {
    "description_contains": "Stop & Shop 0475",
    "employer": "Personal",
    "category": "food",
    "note": ""
  },
  {
    "description_contains": "Bestbuy Totaltech Year",
    "employer": "JVS Management",
    "category": "Subscription",
    "note": ""
  },
  {
    "description_contains": "HLU*Hulu 1858044137764-U",
    "employer": "Personal",
    "category": "entertainment",
    "note": ""
  },
  {
    "description_contains": "JENIS SPLENDID ICE CREAM",
    "employer": "Personal",
    "category": "food",
    "note": ""
  }
]
```

