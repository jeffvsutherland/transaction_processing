import pandas as pd
import json
import os
from datetime import datetime
from rules_processor import RulesProcessor
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set the base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def load_config(config_path):
    with open(config_path, 'r') as f:
        return json.load(f)


def setup_rules_processor(config_path, categories_path):
    # Load the actual configuration
    config = load_config(config_path)

    # Write config and categories to temporary files for RulesProcessor
    temp_config_path = os.path.join(BASE_DIR, 'temp_config.json')
    temp_categories_path = os.path.join(BASE_DIR, 'temp_categories.json')

    with open(temp_config_path, 'w') as f:
        json.dump(config, f)
    with open(temp_categories_path, 'w') as f:
        json.dump({}, f)  # Assuming categories is empty, adjust if needed

    return RulesProcessor(temp_config_path, temp_categories_path), config


def test_starbucks_on_travel_day():
    # Use the actual paths to your config and categories files
    config_path = os.path.join(BASE_DIR, 'config.json')
    categories_path = os.path.join(BASE_DIR, 'categories.json')

    rules_processor, config = setup_rules_processor(config_path, categories_path)

    # Log relevant parts of the configuration
    logger.debug(f"Submitter name: {config['submitter_name']}")
    logger.debug(f"Travel days: {config['employee_rules'][0]['travel_days']}")
    logger.debug(f"Categories expensable on travel: {config['categories_expensable_on_travel']}")
    logger.debug(
        f"Employer rules related to Starbucks: {[rule for rule in config['employer_rules'] if 'starbucks' in rule['description_contains'].lower()]}")

    # Create a DataFrame mimicking the actual data
    df = pd.DataFrame([
        {
            "Date": datetime(2022, 12, 6),
            "Description": "Starbucks",
            "Amount": -5.75,
            "category": "Food",
            "employer": "Personal",
            "Bank": "Crypto.com",
            "Card": "7712"
        }
    ])

    logger.debug(f"Input DataFrame:\n{df}")

    # Apply rules
    result_df = rules_processor.apply_rules(df)

    logger.debug(f"Output DataFrame:\n{result_df}")

    # Assert the expected outcome
    assert result_df.iloc[0]['employer'] == "Frequency Research Foundation", \
        f"Expected employer to be 'Frequency Research Foundation', but got {result_df.iloc[0]['employer']}"
    assert "Travel expense on 2022-12-06" in result_df.iloc[0]['note'], \
        f"Expected note to contain 'Travel expense on 2022-12-06', but got {result_df.iloc[0]['note']}"

    print("Test: Starbucks on travel day (2022-12-06) - Passed")


if __name__ == "__main__":
    try:
        test_starbucks_on_travel_day()
        print("All tests passed successfully!")
    except AssertionError as e:
        logger.error(f"Test failed: {str(e)}")
    finally:
        # Clean up temporary files
        temp_config_path = os.path.join(BASE_DIR, 'temp_config.json')
        temp_categories_path = os.path.join(BASE_DIR, 'temp_categories.json')
        if os.path.exists(temp_config_path):
            os.remove(temp_config_path)
        if os.path.exists(temp_categories_path):
            os.remove(temp_categories_path)