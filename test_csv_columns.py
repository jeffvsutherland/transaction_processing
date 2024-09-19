import os
import pandas as pd

def check_csv_columns(input_dir):
    # List all CSV files in the directory
    csv_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.csv')]

    if not csv_files:
        print(f"No CSV files found in the directory: {input_dir}")
        return

    for csv_file in csv_files:
        filepath = os.path.join(input_dir, csv_file)
        print(f"\nProcessing file: {csv_file}")

        try:
            # Read the CSV file
            df = pd.read_csv(filepath)

            # Print the column names
            print(f"Columns in {csv_file}: {df.columns.tolist()}")

            # Check for the presence of key columns
            expected_columns = {
                'crypto_com': 'Transaction Description',
                'bank_of_america': 'DESCRIPTION',
                'chase': 'Description',
                'capital_one': 'Description'
            }

            # Determine bank type based on filename (this is just a heuristic)
            bank_type = None
            if 'crypto_com' in csv_file.lower():
                bank_type = 'crypto_com'
            elif 'bank' in csv_file.lower():
                bank_type = 'bank_of_america'
            elif 'chase' in csv_file.lower():
                bank_type = 'chase'
            elif 'capitalone' in csv_file.lower():
                bank_type = 'capital_one'

            if bank_type and expected_columns[bank_type] not in df.columns:
                print(f"Warning: Expected column '{expected_columns[bank_type]}' not found in {csv_file}")

            # Print the first few rows to inspect the data
            print(f"First few rows of {csv_file}:\n{df.head()}")

        except Exception as e:
            print(f"Error processing {csv_file}: {e}")

if __name__ == "__main__":
    # Set the directory where your CSV files are located
    input_dir = '/Users/jeffsutherland/Frequency Research Foundation Inc. Dropbox/Frequency Lab/Python/Expenses/chatGPT4o scripts/transaction_processor/input'

    # Run the column check
    check_csv_columns(input_dir)