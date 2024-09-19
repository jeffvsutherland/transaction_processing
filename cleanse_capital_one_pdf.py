import pdfplumber
import csv
import re
import os
from datetime import datetime

# Function to classify transactions as credit or debit
def classify_amount(description, amount):
    credits_keywords = ["autopay", "payment", "credit", "refund"]
    # Check if the description contains any credit-indicating keywords
    if any(keyword.lower() in description.lower() for keyword in credits_keywords):
        return abs(amount)  # Ensure it's positive for credits
    else:
        return -abs(amount)  # Ensure it's negative for debits

# Open the PDF and extract transactions
def extract_transactions_from_pdf(pdf_file):
    transactions = []
    card_last_four = None
    total_lines_parsed = 0  # For debugging and tracking how many lines are parsed

    with pdfplumber.open(pdf_file) as pdf:
        for page_num, page in enumerate(pdf.pages):
            text = page.extract_text()
            if not text:
                continue  # Skip if no text is found

            # Extract the last four digits of the card when available (e.g., "#7931")
            card_match = re.search(r'#(\d{4})', text)
            if card_match:
                card_last_four = card_match.group(1)

            # Regex for "Trans Date Post Date Description Amount"
            pattern = r'(\w{3}\s+\d{1,2})\s+(\w{3}\s+\d{1,2})\s+([A-Za-z0-9\s\*\-]+)\s+([-\$]?\d[\d,]*\.\d{2})'
            matches = re.findall(pattern, text)

            if matches:
                total_lines_parsed += len(matches)
            else:
                print(f"No matches found on page {page_num + 1}. Check the format on this page.")

            for match in matches:
                trans_date, post_date, description, amount = match
                # Clean up the amount, removing $ sign and converting to float
                amount = float(amount.replace('$', '').replace(',', ''))

                # Classify the amount as positive or negative based on description
                amount = classify_amount(description, amount)

                # Append the transaction data
                transactions.append({
                    "Date": post_date.strip(),  # Using post date as the main date
                    "Description": description.strip(),
                    "Amount": amount,
                    "Bank Name": "Capital One",
                    "Card Last Four": card_last_four if card_last_four else "Unknown"
                })

    print(f"Total lines parsed: {total_lines_parsed}")
    return transactions

# Function to write transactions to a CSV file
def write_transactions_to_csv(transactions, output_file):
    # Sort transactions by date (assuming the date format is "Mon Day")
    transactions.sort(key=lambda x: datetime.strptime(x["Date"], "%b %d"))

    with open(output_file, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["Date", "Description", "Amount", "Bank Name", "Card Last Four"])
        writer.writeheader()
        for transaction in transactions:
            writer.writerow(transaction)

    print(f"Transactions successfully written to {output_file}")

# Main execution function
def main():
    # Prompt the user to input the PDF file path
    pdf_file = input("Enter the full path to the PDF file: ").strip()

    # Check if the file exists
    if not os.path.isfile(pdf_file):
        print(f"The file {pdf_file} does not exist. Please provide a valid file path.")
        return

    # Extract transactions from the PDF
    transactions = extract_transactions_from_pdf(pdf_file)

    # Calculate the total number of transactions and the total amount
    total_transactions = len(transactions)
    total_amount = sum(t['Amount'] for t in transactions)

    # Print transaction summary
    print(f"Total number of transactions: {total_transactions}")
    print(f"Total amount: ${total_amount:.2f}")

    # Derive the output CSV file path (same directory as PDF)
    output_file = os.path.splitext(pdf_file)[0] + "_transactions.csv"

    # Write transactions to the CSV file
    write_transactions_to_csv(transactions, output_file)

# Run the main function
if __name__ == "__main__":
    main()
