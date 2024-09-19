import os
import pandas as pd
import logging
from datetime import datetime

def apply_employer_rules(transaction, employer_rules):
    description = str(transaction.get('Description', '')).lower()
    for rule in employer_rules:
        if rule['description_contains'].lower() in description:
            return rule['employer'], rule['category'], rule['note']
    return 'Unknown', 'Uncategorized', ''

def filter_and_categorize_transactions(config, start_date, end_date):
    base_dir = config['base_dir']
    input_dir = os.path.join(base_dir, config['input_dir'])
    output_dir = os.path.join(base_dir, config['output_dir'])
    employer_rules = config['employer_rules']

    # Use a case-insensitive pattern for CSV files
    csv_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.csv')]
    logging.info(f"All files in directory: {os.listdir(input_dir)}")
    logging.info(f"Found bank files: {csv_files}")

    all_transactions = []

    for file in csv_files:
        file_path = os.path.join(input_dir, file)
        logging.info(f"Processing file: {file_path}")

        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            logging.error(f"Error reading file {file}: {str(e)}")
            continue

        logging.info(f"Columns in {file}: {df.columns.tolist()}")

        # Standardize column names
        df.columns = df.columns.str.lower().str.replace(' ', '_')

        # Identify date column
        date_column = next((col for col in df.columns if 'date' in col), None)
        if date_column is None:
            logging.warning(f"No date column found in {file}. Skipping this file.")
            continue

        # Convert date to datetime
        df[date_column] = pd.to_datetime(df[date_column], errors='coerce')

        # Filter data within date range
        mask = (df[date_column] >= start_date) & (df[date_column] <= end_date)
        filtered_df = df.loc[mask].copy()

        logging.info(f"Filtered data within date range for {file}")

        # Standardize and select required columns
        if 'description' not in filtered_df.columns:
            filtered_df['description'] = filtered_df.get('transaction_description', filtered_df.get('memo', ''))

        if 'amount' not in filtered_df.columns:
            filtered_df['amount'] = filtered_df.get('debit', filtered_df.get('credit', filtered_df.get('amount.1', 0)))

        # Select and rename columns
        filtered_df = filtered_df.rename(columns={date_column: 'date'})
        filtered_df['source_file'] = file

        # Apply employer rules and add new columns
        filtered_df[['employer', 'category', 'note']] = filtered_df.apply(
            lambda row: pd.Series(apply_employer_rules(row, employer_rules)), axis=1
        )

        # Select final columns
        final_columns = ['date', 'description', 'amount', 'employer', 'category', 'note', 'source_file']
        filtered_df = filtered_df[final_columns]

        output_file = os.path.join(output_dir, f"{os.path.splitext(file)[0]}_filtered.csv")
        filtered_df.to_csv(output_file, index=False)
        logging.info(f"Saved filtered data to {output_file}")

        all_transactions.append(filtered_df)

    if not all_transactions:
        logging.error("No transactions found in any file.")
        return pd.DataFrame()

    logging.info("Concatenating all transactions")
    merged_df = pd.concat(all_transactions, ignore_index=True)

    # Sort by date
    merged_df = merged_df.sort_values('date')

    merged_file = os.path.join(output_dir, "merged_transactions.csv")
    merged_df.to_csv(merged_file, index=False)
    logging.info(f"Merged DataFrame saved to {merged_file}")

    return merged_df