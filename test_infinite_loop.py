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
    for col in df.columns:
        if 'date' in col.lower():
            return col
    raise ValueError("No date column found")

def process_bank_file(filepath, config, output_dir):
    bank_name = os.path.basename(filepath).replace('.csv', '')
    log(f"Processing file: {bank_name}")

    df = pd.read_csv(filepath)
    log(f"Available columns in {bank_name}: {list(df.columns)}")

    try:
        date_column = find_date_column(df)
        start_date = config['start_date']
        end_date = config['end_date']
        df[date_column] = pd.to_datetime(df[date_column])
        df = df[(df[date_column] >= start_date) & (df[date_column] <= end_date)]
        df['Bank'] = bank_name

        if 'Card No.' in df.columns:
            df['Card Last Four'] = df['Card No.'].astype(str).apply(lambda x: x[-4:])
        else:
            df['Card Last Four'] = 'Unknown'

        log(f"Extracted Card Last Four for {bank_name}: {df['Card Last Four'].unique()}")

        if 'Card No.' in df.columns:
            df.drop(columns=['Card No.'], inplace=True)

        intermediate_file_path = os.path.join(output_dir, f"intermediate_{bank_name}.csv")
        df.to_csv(intermediate_file_path, index=False)
        log(f"Intermediate file saved at: {intermediate_file_path}")

        # Print the intermediate file to the console
        print(df)

        return df
    except Exception as e:
        log(f"Error processing {bank_name}: {str(e)}")
        return None

config = {
    'start_date': '2022-10-26',
    'end_date': '2022-10-27',
    'output_dir': 'output'
}

data = {
    'Transaction Description': ['Purchase', 'Refund'],
    'Normalized Date': ['2022-10-26', '2022-10-27'],
    'Amount': [100, -50],
    'Currency': ['USD', 'USD'],
    'Card No.': ['1234567812341234', '5678567856785678']
}

mock_csv_path = 'mock_bank_file.csv'
df = pd.DataFrame(data)
df.to_csv(mock_csv_path, index=False)

os.makedirs(config['output_dir'], exist_ok=True)

processed_df = process_bank_file(mock_csv_path, config, config['output_dir'])

print(processed_df[['Bank', 'Card Last Four']])

os.remove(mock_csv_path)