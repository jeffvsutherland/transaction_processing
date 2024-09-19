import pandas as pd
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def print_dataframe(df, message):
    logger.info(message)
    logger.info("\n" + df.to_string())
    logger.info("\n")

def test_manual_transaction_merge():
    # Sample bank transactions
    bank_transactions = pd.DataFrame({
        'Date': ['2022-12-01', '2022-12-02'],
        'Description': ['Bank Transaction 1', 'Bank Transaction 2'],
        'Amount': ['100.00', '200.00'],
        'Bank': ['Bank A', 'Bank B'],
        'Card': ['1234', '5678'],
        'employer': ['Unknown', 'Unknown'],
        'category': ['Uncategorized', 'Uncategorized'],
        'note': ['', ''],
        'Vendor': ['Vendor 1', 'Vendor 2']
    })

    # Sample manual transaction
    manual_transaction = pd.DataFrame({
        'Date': ['2022-12-06'],
        'Description': ['Car travel: 100 Page Road, Lincoln MA to 2 Mockingbird Lane, Harwich MA (98.30 miles)'],
        'Amount': ['61.44'],
        'Bank': ['Manual Entry'],
        'Card': ['Manual'],
        'employer': ['Frequency Research Foundation'],
        'category': ['Travel'],
        'note': ['IRS standard mileage rate applied for 2022'],
        'Vendor': ['Car travel: 100 Page Road, Lincoln MA to 2 Mockingbird Lane, Harwich MA (98.30 miles)']
    })

    print_dataframe(bank_transactions, "Bank Transactions:")
    print_dataframe(manual_transaction, "Manual Transaction:")

    # Merge transactions
    merged_df = pd.concat([bank_transactions, manual_transaction], ignore_index=True)

    print_dataframe(merged_df, "Merged Transactions:")

    # Check if manual transaction retained its values
    manual_in_merged = merged_df[merged_df['Bank'] == 'Manual Entry']
    print_dataframe(manual_in_merged, "Manual Transaction in Merged DataFrame:")

    # Verify if employer and category are preserved
    is_preserved = (manual_in_merged['employer'].iloc[0] == 'Frequency Research Foundation' and
                    manual_in_merged['category'].iloc[0] == 'Travel')

    if is_preserved:
        logger.info("SUCCESS: Manual transaction employer and category are preserved.")
    else:
        logger.error("FAILURE: Manual transaction employer and category are not preserved.")
        logger.error(f"Employer: {manual_in_merged['employer'].iloc[0]}")
        logger.error(f"Category: {manual_in_merged['category'].iloc[0]}")

if __name__ == "__main__":
    test_manual_transaction_merge()