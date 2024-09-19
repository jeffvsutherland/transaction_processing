import os
import pandas as pd
import logging
from rules_processor import RulesProcessor

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_refund_transaction():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, 'config.json')
    categories_path = os.path.join(base_dir, 'categories.json')

    # Initialize RulesProcessor
    rules_processor = RulesProcessor(config_path, categories_path)

    # Create a test transaction
    test_transaction = pd.DataFrame({
        'Date': ['2022-10-15'],
        'Description': ['REFUND: Scrum Inc Course'],
        'Amount': [1000.00],
        'Bank': ['Test Bank'],
        'Card': ['1234'],
        'employer': ['Unknown'],
        'category': ['Uncategorized'],
        'note': [''],
        'Vendor': ['Scrum Inc']
    })

    # Apply rules to the test transaction
    processed_transaction = rules_processor.apply_rules(test_transaction)

    # Check if the transaction is correctly categorized
    if processed_transaction.iloc[0]['employer'] == 'Personal' and processed_transaction.iloc[0]['category'] == 'Refund':
        logger.info("Test passed: Refund transaction correctly categorized as Personal")
    else:
        logger.error(f"Test failed: Refund transaction incorrectly categorized. "
                     f"Employer: {processed_transaction.iloc[0]['employer']}, "
                     f"Category: {processed_transaction.iloc[0]['category']}")

    # Print the processed transaction for debugging
    logger.debug(f"Processed transaction: {processed_transaction.to_dict('records')[0]}")

if __name__ == "__main__":
    test_refund_transaction()