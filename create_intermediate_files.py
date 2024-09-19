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

def find_date_column(df):
    # Implement logic to find the date column
    pass

def process_bank_file(filepath, config, output_dir):
    bank_name = os.path.basename(filepath)
    log(f"Processing file: {bank_name}")

    df = pd.read_csv(filepath)
    log(f"Available columns in {bank_name}: {list(df.columns)}")

    try:
        date_column = find_date_column(df)
        start_date = config['start_date']
        end_date = config['end_date']
        df = df[(df[date_column] >= start_date) & (df[date_column] <= end_date)]
        df['Bank'] = bank_name

        if 'Transaction Description' in df.columns:
            df['Vendor'] = df['Transaction Description']
        elif 'Description' in df.columns:
            df['Vendor'] = df['Description']
        elif 'Details' in df.columns:  # Handle Bank of America
            df['Vendor'] = df['Details']
        else:
            df['Vendor'] = 'Unknown'

        # Handle cases where Vendor is still 'Unknown'
        if df['Vendor'].isna().any() or (df['Vendor'] == 'Unknown').any():
            df['Vendor'] = df.apply(lambda row: row['Details'] if pd.notna(row['Details']) else 'Unknown', axis=1)

        # Extract last four digits from the Bank of America CSV file name
        if 'Bank America' in bank_name:
            df['Card Last Four'] = bank_name.split()[-1][:4]
        elif 'crypto_com' in bank_name:
            df['Card Last Four'] = bank_name.split()[-1][:4]
        elif 'Card No.' in df.columns:
            df['Card Last Four'] = df['Card No.'].astype(str).apply(lambda x: x[-4:])
        else:
            df['Card Last Four'] = 'Unknown'

        # Log the extracted Card Last Four values
        log(f"Extracted Card Last Four for {bank_name}: {df['Card Last Four'].unique()}")

        # Save intermediate file
        intermediate_file_path = os.path.join(output_dir, f"intermediate_{bank_name}")
        df.to_csv(intermediate_file_path, index=False)
        log(f"Intermediate file saved at: {intermediate_file_path}")

        return df
    except Exception as e:
        log(f"Error processing {bank_name}: {str(e)}")
        return None