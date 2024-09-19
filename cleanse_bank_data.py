import os
import csv
from datetime import datetime
import re

def parse_date(date_string):
    date_formats = ['%Y-%m-%d %H:%M:%S', '%m/%d/%y', '%m/%d/%Y', '%Y-%m-%d']
    for fmt in date_formats:
        try:
            return datetime.strptime(date_string, fmt).date()
        except ValueError:
            continue
    print(f"Warning: Unable to parse date: {date_string}")
    return None

def parse_amount(amount_string):
    try:
        amount = float(amount_string.replace('$', '').replace(',', ''))
        return -amount  # Make all amounts negative for expenses
    except ValueError:
        print(f"Error parsing amount: {amount_string}")
        return None

def detect_columns(headers):
    columns = {}
    for i, header in enumerate(headers):
        header_lower = header.lower()
        if 'date' in header_lower:
            columns['date'] = i
        elif 'description' in header_lower:
            columns['description'] = i
        elif 'amount' in header_lower:
            columns['amount'] = i
    return columns

def extract_card_number(filename):
    # Look for a pattern like "CapitalOne 7931" or similar
    match = re.search(r'(?:CapitalOne|Chase|Amex)\s+(\d{4})', filename, re.IGNORECASE)
    if match:
        return match.group(1)
    return "Unknown"

def process_bank_file(input_file_path):
    transactions = []
    original_count = 0
    original_total = 0.0

    # Generate output file name
    directory, filename = os.path.split(input_file_path)
    name, ext = os.path.splitext(filename)
    output_file_path = os.path.join(directory, f"{name}_processed{ext}")

    # Extract card number from filename
    card_number = extract_card_number(name)

    # Determine bank name from filename
    bank_name = 'Capital One' if 'capitalone' in name.lower() else 'Unknown Bank'

    # Read the input CSV file
    with open(input_file_path, 'r', encoding='utf-8-sig') as csvfile:
        reader = csv.reader(csvfile)
        headers = next(reader)
        print("Detected columns:", headers)

        columns = detect_columns(headers)
        print("Column mapping:", columns)

        required_columns = ['date', 'description', 'amount']
        if not all(col in columns for col in required_columns):
            print("Error: Required columns not found in the CSV file.")
            return

        for row in reader:
            if len(row) != len(headers):
                print(f"Skipping malformed row: {row}")
                continue

            original_count += 1
            date = parse_date(row[columns['date']])
            amount = parse_amount(row[columns['amount']])

            if amount is not None:
                original_total += amount

            if date:
                transactions.append({
                    'Date': date,
                    'Description': row[columns['description']].strip(),
                    'Amount': amount,
                    'Bank': bank_name,
                    'Card': card_number
                })
            else:
                print(f"Skipping row with missing or invalid data: {row}")

    # Sort transactions by date
    transactions.sort(key=lambda x: x['Date'])

    # Write to the output CSV file
    with open(output_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Date', 'Description', 'Amount', 'Bank', 'Card']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for transaction in transactions:
            writer.writerow({
                'Date': transaction['Date'].strftime('%Y-%m-%d'),
                'Description': transaction['Description'],
                'Amount': f"{transaction['Amount']:.2f}" if transaction['Amount'] is not None else "",
                'Bank': transaction['Bank'],
                'Card': transaction['Card']
            })

    processed_count = len(transactions)
    processed_total = sum(t['Amount'] for t in transactions if t['Amount'] is not None)

    print(f"Original transactions: {original_count}")
    print(f"Original total amount: ${original_total:.2f}")
    print(f"Processed transactions: {processed_count}")
    print(f"Processed total amount: ${processed_total:.2f}")
    print(f"Output written to {output_file_path}")

    if abs(original_total - processed_total) > 0.01:
        print("Warning: Total amount mismatch!")
        print(f"Difference: ${abs(original_total - processed_total):.2f}")

    return transactions, output_file_path

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        input_file_path = sys.argv[1]
    else:
        input_file_path = input("Enter the full path of the CSV file to process: ").strip()

    if not os.path.isfile(input_file_path):
        print("Error: Invalid file path.")
        sys.exit(1)

    process_bank_file(input_file_path)