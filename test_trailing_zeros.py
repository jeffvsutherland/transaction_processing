import pandas as pd

# Sample data to mimic the issue
data = {
    'Date': ['2022-10-01', '2022-10-02', '2022-10-03'],
    'Description': ['Transaction 1', 'Transaction 2', 'Transaction 3'],
    'Amount': [123.40, 56.00, 78.90],
    'Bank': ['Bank A', 'Bank B', 'Bank C'],
    'Card': ['1234', '5678', '9101']
}

# Create DataFrame
df = pd.DataFrame(data)

# Ensure Amount is formatted to always show two decimal places as a string
df['Amount'] = df['Amount'].apply(lambda x: f"{x:.2f}")

# Print DataFrame to see if zeroes are preserved
print(df)

# Manually construct the markdown table
header = "| Date       | Description   |   Amount | Bank   |   Card |"
separator = "|:-----------|:--------------|---------:|:-------|-------:|"
rows = "\n".join(
    f"| {row['Date']} | {row['Description']} | {row['Amount']} | {row['Bank']} | {row['Card']} |"
    for index, row in df.iterrows()
)

report = "\n".join([header, separator, rows])
print(report)