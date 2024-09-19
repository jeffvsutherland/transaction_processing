import pandas as pd
import json


def load_config(config_path):
    with open(config_path, 'r') as f:
        return json.load(f)


def load_transactions(file_path):
    return pd.read_csv(file_path)


def generate_employer_expense_report(df, employer):
    df = df[df['employer'] == employer].copy()

    # Convert 'Date' column to datetime if it's not already
    if df['Date'].dtype != 'datetime64[ns]':
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

    # Ensure 'category' column contains simple values
    if df['category'].dtype == 'object':
        df['category'] = df['category'].apply(lambda x: x.iloc[0] if isinstance(x, pd.Series) else x)

    # Sort the DataFrame
    df = df.sort_values(['category', 'Date'])

    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').apply(lambda x: f"{x:.2f}")

    grouped = df.groupby('category')
    for category, group in grouped:
        print(f"Category: {category}")
        print(group[['Date', 'Description', 'Amount', 'Bank', 'Card', 'note']])
        print("\nTesting 'note' column:")
        print("Is 'note' in columns?", 'note' in group.columns)
        if 'note' in group.columns:
            print("Any non-null values?", not group['note'].isna().all())
            print("Any non-empty strings?", group['note'].astype(str).str.strip().any())
            print("Unique values in 'note':", group['note'].unique())
        print("\n")


def main():
    config_path = 'config.json'
    transactions_path = 'output/merged_transactions.csv'

    config = load_config(config_path)
    df = load_transactions(transactions_path)

    for employer in config.get('employers', []):
        print(f"\nProcessing employer: {employer}")
        generate_employer_expense_report(df, employer)


if __name__ == "__main__":
    main()