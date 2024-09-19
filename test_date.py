import pandas as pd

# Simulate the DataFrame with a Timestamp (UTC) column
data = {
    'Timestamp (UTC)': ['2022-10-01 00:00:00', '2022-10-02 00:00:00'],
    'Transaction Description': ['Purchase at Store A', 'Purchase at Store B'],
    'Amount': [100, 200]
}

df = pd.DataFrame(data)

# Convert 'Timestamp (UTC)' to datetime
df['Timestamp (UTC)'] = pd.to_datetime(df['Timestamp (UTC)'])

# Print the columns
print("Available columns:", df.columns.tolist())

# The find_date_column function
def find_date_column(df):
    print("Checking for date columns in the data...")
    print("Available columns:", df.columns.tolist())

    possible_columns = ['Transaction Date', 'Timestamp', 'Date', 'DateTime', 'Transaction DateTime']

    for col in possible_columns:
        if col in df.columns:
            print(f"Found potential date column: {col}")
            if 'Timestamp' in col or 'DateTime' in col:
                df['Transaction Date'] = pd.to_datetime(df[col]).dt.date
                df['Transaction Time'] = pd.to_datetime(df[col]).dt.time
                return 'Transaction Date'
            return col

    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            print(f"Found datetime type column: {col}")
            df['Transaction Date'] = pd.to_datetime(df[col]).dt.date
            df['Transaction Time'] = pd.to_datetime(df[col]).dt.time
            return 'Transaction Date'

    print("No valid date column found.")
    raise ValueError("No valid date column found in the data.")

# Invoke the function
date_column = find_date_column(df)
print(f"Date column used: {date_column}")